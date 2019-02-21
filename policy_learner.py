import os
import locale
import logging
import numpy as np
import settings
from environment import Environment
from agent import Agent
from policy_network import PolicyNetwork
from visualizer import Visualizer


logger = logging.getLogger(__name__)
locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')


class PolicyLearner:

    def __init__(self, stock_code, chart_data, training_data=None,
                 min_trading_unit=1, max_trading_unit=2,
                 delayed_reward_threshold=.05, lr=0.01):
        self.stock_code = stock_code  # 종목코드
        self.chart_data = chart_data
        self.environment = Environment(chart_data)  # 환경 객체
        # 에이전트 객체
        self.agent = Agent(self.environment,
                           min_trading_unit=min_trading_unit,
                           max_trading_unit=max_trading_unit,
                           delayed_reward_threshold=delayed_reward_threshold)
        self.training_data = training_data  # 학습 데이터
        self.sample = None
        self.training_data_idx = -1
        # 정책 신경망; 입력 크기 = 학습 데이터의 크기 + 에이전트 상태 크기
        self.num_features = self.training_data.shape[1] + self.agent.STATE_DIM
        self.policy_network = PolicyNetwork(
            input_dim=self.num_features, output_dim=self.agent.NUM_ACTIONS, lr=lr)
        self.visualizer = Visualizer()  # 가시화 모듈

    def reset(self):
        self.sample = None
        self.training_data_idx = -1

    def fit(
        self, num_epoches=1000, max_memory=60, balance=10000000,
        discount_factor=0, start_epsilon=.5, learning=True):
        logger.info("LR: {lr}, DF: {discount_factor}, "
                    "TU: [{min_trading_unit}, {max_trading_unit}], "
                    "DRT: {delayed_reward_threshold}".format(
            lr=self.policy_network.lr,
            discount_factor=discount_factor,
            min_trading_unit=self.agent.min_trading_unit,
            max_trading_unit=self.agent.max_trading_unit,
            delayed_reward_threshold=self.agent.delayed_reward_threshold
        ))

        # 가시화 준비
        # 차트 데이터는 변하지 않으므로 미리 가시화
        self.visualizer.prepare(self.environment.chart_data)

        # 가시화 결과 저장할 폴더 준비
        epoch_summary_dir = os.path.join(
            settings.BASE_DIR, 'epoch_summary/%s/epoch_summary_%s' % (
                self.stock_code, settings.timestr))                         ## settings.timestr = 20190122230703
        if not os.path.isdir(epoch_summary_dir):
            os.makedirs(epoch_summary_dir)

        # 에이전트 초기 자본금 설정
        self.agent.set_balance(balance)

        # 학습에 대한 정보 초기화
        max_portfolio_value = 0                 # 학습중에 발생한 최대 포트폴리오의 값을 저장.
        epoch_win_cnt = 0                       # 학습중에 수익이 발생한 에포크의 수를 저장.

        # 학습 반복
        for epoch in range(num_epoches):    
            # 에포크 관련 정보 초기화
            loss = 0.                           # 정책신경망의 결과가 학습데이터와의 차이. 학습이 진행되면서  줄어 드는 것이 좋다.
            itr_cnt = 0                         # 수행한 에포크 수를 저장합니다.
            win_cnt = 0                         # 수행한 에포크 중에서 수익이 발생한 에포크 수
            exploration_cnt = 0                 # 무작위 투자를 수행한 회수.
            batch_size = 0
            pos_learning_cnt = 0                # 수익이 발생하여 긍정적으로 지연보상을 수행한 회수
            neg_learning_cnt = 0                # 손실이 발생하여 부정적으로 지연보상을 수행한 회수

            # 메모리 초기화
            memory_sample = []
            memory_action = []
            memory_reward = []
            memory_prob = []
            memory_pv = []
            memory_num_stocks = []
            memory_exp_idx = []
            memory_learning_idx = []
            
            # 환경, 에이전트, 정책 신경망 초기화
            self.environment.reset()
            self.agent.reset()
            self.policy_network.reset()
            self.reset()

            # 가시화 초기화
            self.visualizer.clear([0, len(self.chart_data)])        # x축 데이터 범위를 전달.

            # 학습을 진행할 수록 탐험 비율 감소
            # start_epsilon : 초기 탐험 비율, 초기에는 탐험비율을 크게 해서, 무작위 투자를 수행.
            # learning : true : 정책 신경망을 만들려고 할 겨우,
            #          : false : 만들어진 신경망으로 투자 시뮬레이션만 할 경우.
            if learning:
                epsilon = start_epsilon * (1. - float(epoch) / (num_epoches - 1))
            else:
                epsilon = 0

            while True:                             # 하나의 epoch을 수행.
                # 샘플 생성
                next_sample = self._build_sample()
                if next_sample is None:             # 마지막 data까지 읽었서 data가 없을 경우  none 이다.
                    break

                # 정책 신경망 또는 탐험에 의한 행동 결정
                action, confidence, exploration = self.agent.decide_action(self.policy_network, self.sample, epsilon)
                    # action : 매도,매수, confidence:확신도, exploration:무작위여부,

                # 결정한 행동을 수행하고 즉시 보상과 지연 보상 획득
                immediate_reward, delayed_reward = self.agent.act(action, confidence)       # 실제 실행.

                # 행동 및 행동에 대한 결과를 기억
                memory_sample.append(next_sample)
                memory_action.append(action)
                memory_reward.append(immediate_reward)
                memory_pv.append(self.agent.portfolio_value)
                memory_num_stocks.append(self.agent.num_stocks)
                memory = [(memory_sample[i],memory_action[i],memory_reward[i])for i in list(range(len(memory_action)))[-max_memory:]]
                if exploration:
                    memory_exp_idx.append(itr_cnt)                          # 무작위 투자인 경우, index을 저장한다.
                    memory_prob.append([np.nan] * Agent.NUM_ACTIONS)        # 정책신경망의 결과를 그대로 저장,  그러나, 무작위이므로, NAN을 사용한다.
                else:
                    memory_prob.append(self.policy_network.prob)            # 정책신경망의 결과를 그대로 저장,

                # 반복에 대한 정보 갱신
                batch_size += 1
                itr_cnt += 1
                exploration_cnt += 1 if exploration else 0
                win_cnt += 1 if delayed_reward > 0 else 0                   # 수익이 발생한 경우, count-up.

                # 학습 모드이고 지연 보상이 존재할 경우 정책 신경망 갱신
                if delayed_reward == 0 and batch_size >= max_memory:
                    delayed_reward = immediate_reward
                    self.agent.base_portfolio_value = self.agent.portfolio_value

                if learning and delayed_reward != 0:                        # 학습모드이고, 지연보상이 있는 경우.
                    # 배치 학습 데이터 크기
                    batch_size = min(batch_size, max_memory)
                    # 배치 학습 데이터 생성
                    # discount_factor : 과거로 갈수록 지연보상을 적게 적용할 할인 요인.
                    x, y = self._get_batch(memory, batch_size, discount_factor, delayed_reward)
                    if len(x) > 0:
                        if delayed_reward > 0:
                            pos_learning_cnt += 1
                        else:
                            neg_learning_cnt += 1
                        # 정책 신경망 갱신
                        loss += self.policy_network.train_on_batch(x, y)        # batch data 으로 학습 진행.
                        memory_learning_idx.append([itr_cnt, delayed_reward])
                    batch_size = 0

            # 1개의 에포크가 완성,  관련 정보 가시화
            num_epoches_digit = len(str(num_epoches))
            epoch_str = str(epoch + 1).rjust(num_epoches_digit, '0')            # 4자리 수자표시, 앞은 0으로 채운다.

            self.visualizer.plot(
                epoch_str=epoch_str, num_epoches=num_epoches, epsilon=epsilon,
                action_list=Agent.ACTIONS, actions=memory_action,
                num_stocks=memory_num_stocks, outvals=memory_prob,
                exps=memory_exp_idx, learning=memory_learning_idx,
                initial_balance=self.agent.initial_balance, pvs=memory_pv
            )

            self.visualizer.save(os.path.join(epoch_summary_dir, 'epoch_summary_%s_%s.png' % (settings.timestr, epoch_str)))

            # 에포크 관련 정보 로그 기록
            if pos_learning_cnt + neg_learning_cnt > 0:
                loss /= pos_learning_cnt + neg_learning_cnt

            logger.info("[Epoch %s/%s]\tEpsilon:%.4f\t#Expl.:%d/%d\t"
                        "#Buy:%d\t#Sell:%d\t#Hold:%d\t"
                        "#Stocks:%d\tPV:%s\t"
                        "POS:%s\tNEG:%s\tLoss:%10.6f" % (
                            epoch_str, num_epoches, epsilon, exploration_cnt, itr_cnt,
                            self.agent.num_buy, self.agent.num_sell, self.agent.num_hold,
                            self.agent.num_stocks,
                            locale.currency(self.agent.portfolio_value, grouping=True),
                            pos_learning_cnt, neg_learning_cnt, loss))

            # 1개의 에포크가 끝났으므로, 학습 관련 정보 갱신
            max_portfolio_value = max( max_portfolio_value, self.agent.portfolio_value)
            if self.agent.portfolio_value > self.agent.initial_balance:
                epoch_win_cnt += 1

        # 학습 관련 정보 로그 기록
        logger.info("Max PV: %s, \t # Win: %d" % (locale.currency(max_portfolio_value, grouping=True), epoch_win_cnt))

    def _get_batch(self, memory, batch_size, discount_factor, delayed_reward):
        x = np.zeros((batch_size, 1, self.num_features))
        y = np.full((batch_size, self.agent.NUM_ACTIONS), 0.5)

        for i, (sample, action, reward) in enumerate(reversed(memory[-batch_size:])):
            x[i] = np.array(sample).reshape((-1, 1, self.num_features))
            y[i, action] = (delayed_reward + 1) / 2
            if discount_factor > 0:
                y[i, action] *= discount_factor ** i
        return x, y

    def _build_sample(self):
        self.environment.observe()
        if len(self.training_data) > self.training_data_idx + 1:
            self.training_data_idx += 1
            self.sample = self.training_data.iloc[self.training_data_idx].tolist()
            self.sample.extend(self.agent.get_states())
            return self.sample
        return None

    def trade(self, model_path=None, balance=2000000):
        if model_path is None:
            return
        self.policy_network.load_model(model_path=model_path)
        self.fit(balance=balance, num_epoches=1, learning=False)
