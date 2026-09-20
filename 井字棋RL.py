import numpy as np

class state:
    def __init__(self):
        self.data=np.zeros((3,3), dtype=int)
        self.winner=None
        self.hash_val=0
        self.end=False

    def hash(self):
        t=self.data.reshape(9)
        self.hash_val=0
        for i in range(9):
            self.hash_val+=(3**i)*(t[i]+1)
        return self.hash_val
        #type of hash_val is np.int64

    def is_end(self):
        multy=1
        for i in range(3):
            for j in range(3):
                multy*=self.data[i][j]
        self.end=bool(multy!=0)
        result=[]
        for i in range(3):
            result.append(np.sum(self.data[i,:]))
        for i in range(3):
            result.append(np.sum(self.data[:,i]))
        x,y=0,0
        for i in range(3):
            x+=self.data[i][i]
            y+=self.data[i][2-i]
        result.append(x)
        result.append(y)
        for i in result:
            if i==3 or i==-3:
                self.end=True
                self.winner=int(np.sign(i))   # 1: 先手方(X)胜, -1: 后手方(O)胜
                break
        return self.end


    def next_state(self,i,j,symbol):
        #注意不能直接修改原来的self.state,应该先复制一份
        new_state=state()
        new_state.data=self.data.copy()   #数组的 .copy() 就是深拷贝内容，不需要再套 np.copy
        new_state.data[i,j]=symbol
        return new_state

    def print_state(self):
        print(self.data)


#建立所有状态的hash映射
def get_next(current_state,current_symbol,all_states):
    for i in range(3):
        for j in range(3):
            if current_state.data[i,j]==0:
                new_state=current_state.next_state(i,j,current_symbol)
                new_hash=new_state.hash()
                if new_hash not in all_states.keys():
                    all_states[new_hash]=(new_state,new_state.is_end())
                    if not new_state.is_end():
                        get_next(new_state,-current_symbol,all_states)
    return all_states

beginning=state()

all_states=get_next(beginning,1,{beginning.hash():(beginning,beginning.is_end())})


#机器玩家
class Player:
    def __init__(self,symbol,step_size=0.1,epsilon=0.1):
        self.estimations=dict()
        self.step_size=step_size
        self.epsilon=epsilon
        self.states=[]
        self.greedy=[]
        self.symbol=symbol

    def reset(self):
        self.states=[]
        self.greedy=[]
    def set_state(self,state):
        self.states.append(state)
        self.greedy.append(True)

    #定义末状态的估值，由此确定学习的方向
    def set_goal(self,symbol):
        for hash_val in all_states.keys():
            state,is_end=all_states[hash_val]
            if is_end:
                if state.winner==symbol:
                    self.estimations[hash_val]=1
                # is_end() 只在连成三子时给 winner 赋值，平局时 winner 是 None 而不是 0，
                # 所以原来这里写 winner==0 永远不成立，平局终局被当成"输"赋成 0
                elif state.winner is None:
                    self.estimations[hash_val]=0.5
                else:self.estimations[hash_val]=0
            else:self.estimations[hash_val]=0.5

    def update(self):
        states=[state.hash() for state in self.states]#self.states还没有定义
        for i in reversed(range(len(states)-1)):
            td_error=self.greedy[i]*(self.estimations[states[i+1]]-self.estimations[states[i]])
            self.estimations[states[i]]+=td_error*self.step_size

    def act(self):#generate (i,j,symbol)
        state=self.states[-1]#why is -1??
        # need to focus on empty set!!!
        next_position=[]
        next_state=[]
        for i in range(3):
            for j in range(3):
                if state.data[i,j]==0:
                    next_position.append([i,j])
                    next_state.append(state.next_state(i,j,self.symbol))
        if np.random.rand()<self.epsilon:
            action=next_position[np.random.randint(len(next_position))]
            action.append(self.symbol)
            self.greedy[-1]=False#random actions should not be included into updates of estimations
            return action
        values=[]
        for stat,posi in zip(next_state,next_position):
            values.append((self.estimations[int(stat.hash())],posi))
            #key of self.estimations is in type of int64,attribute to typeerror
        np.random.shuffle(values)
        values.sort(key=lambda x:x[0])
        action=values[-1][1]
        action.append(self.symbol)
        return action

#两个机器玩家互相训练
def train(epos,p1,p2):#set_state act update reset
    for i in range(epos):
        p1.reset()
        p2.reset()
        current_state=state()
        p1.set_state(current_state)
        p2.set_state(current_state)
        while not current_state.is_end():
            sig=current_state.data.sum()
            if sig==0:
                a=p1.act()
                current_state=current_state.next_state(a[0],a[1],a[2])
            else:
                b=p2.act()
                current_state=current_state.next_state(b[0],b[1],b[2])#new created!
            p1.set_state(current_state)
            p2.set_state(current_state)
            p1.update()
            p2.update()
    print('training completed')


def compete():
    p2.epsilon=0
    p2.reset()                    # 清掉训练留下的 states，让 p2 只认下面喂给它的盘面
    curstate=state()
    turn=0
    print('你是 X, 请落子: q w e / a s d / z x c')
    curstate.print_state()
    while not curstate.is_end():
        if turn%2==0:
            human_play(curstate)
        else:
            p2.set_state(curstate)        # 关键：act() 从 states[-1] 取盘面，必须先喂进去
            a=p2.act()
            curstate.data[a[0],a[1]]=a[2]
        curstate.is_end()                 # 刷新 end / winner
        curstate.print_state()
        print('-'*8)
        turn+=1
    judge(curstate)
    compete()  #自身迭代，实现重复对局


def human_play(state):
    key=input('type your position:')
    diction={'q':[0,0],'w':[0,1],'e':[0,2],'a':[1,0],'s':[1,1],'d':[1,2],'z':[2,0],'x':[2,1],'c':[2,2]}
    while key not in diction or state.data[diction[key][0]][diction[key][1]]!=0:
        if key not in diction:
            print('无效按键, 请用 q w e a s d z x c')
        else:
            print('这个位置已经有子了, 换一个')
        key=input('type your position:')
    state.data[diction[key][0]][diction[key][1]]=1

def judge(state):
    state.is_end()
    if state.winner==1:
        print('you win')
    elif state.winner==-1:
        print('you lose')
    else:
        print('It is a tie')

p1=Player(1)
p2=Player(-1)
p1.set_goal(1)
p2.set_goal(-1)
train(100000,p1,p2)
compete()


    
        
                    
        
    
        





