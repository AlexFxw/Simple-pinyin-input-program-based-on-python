from file_loader import Analyzer
import re
from pypinyin import lazy_pinyin
import math
import sys

c_num = 20
alpha = 0.1 
beta = 1 - alpha
min_num = -100000

class node:
    def __init__(self):
        self.s = '' 
        self.f = 0.0

class Calculator:
    def __init__(self,a):
        self.analyzer = a
        self.pb_dict = {} 
        self.pinyin = []
        self.ans_sentence = {}
        self.ans_dict = {}
        self.ans = []
        self.ans_list = []
        self.word_cnt = 0
        self.stc_cnt = 0
    def read_in(self, path):
        with open (path, 'r') as f:
            for line in f.readlines():
                cur_str = re.sub('\n', '', line)
                self.pinyin.append(re.split(' ', cur_str))
    def read_ans(self, path):
        with open (path, 'r') as f:
            for line in f.readlines():
                cur_str = re.sub('\n', '', line)
                self.ans.append(cur_str)
    def test(self, path):
        with open(path, 'r') as f:
            l = 0
            for line in f.readlines():
                cur_str = re.sub(' \n|  \n|\n', '', line)
                if l == 0:
                    self.pinyin.append(re.split(' ', cur_str))
                    l = 1
                elif l == 1:
                    cur_stc = re.sub(' ', '', cur_str)
                    self.ans.append(cur_stc)
                    l = 0
        self.viterbi()
        lth = min(len(self.ans), len(self.ans_list))
        stc_num = 0
        wd_num = 0
        for i in range(0, lth):
            if self.cmp_stc(self.ans_list[i], self.ans[i]):
                print('correct: ' + self.ans_list[i])
                stc_num = stc_num + 1
            else:
                print('wrong: ' + self.ans_list[i] + '/ ' + self.ans[i])
            wd_num = wd_num + self.cmp_word(self.ans_list[i], self.ans[i])
        print('句子正确率：' + str(stc_num/self.stc_cnt))
        print('字正确率：' + str(wd_num/self.word_cnt))
    def cmp_stc(self, str_1, str_2):
        self.stc_cnt = self.stc_cnt + 1 
        if str_1 == str_2:
            return True
        return False
    def cmp_word(self, str_1, str_2):
        l = min(len(str_2), len(str_1))
        self.word_cnt = self.word_cnt + l
        cnt = 0
        for i in range(0,l):
            if str_1[i] == str_2[i]:
                cnt = cnt + 1
        return cnt
    def viterbi(self):
        k = 0
        total = len(self.pinyin) - 1
        for py_list in self.pinyin:
            l = len(py_list)
            self.pb_dict = {} 
            self.ans_sentence = {}
            self.ans_dict = {}
            if l == 1:
                cur_list = self.analyzer.find_choice(py_list[l-1].lower(), 1)
                ans_nd = node()
                ans_nd.s = cur_list[0][0] 
            else:
                for i in range(1, l):
                    last_py = py_list[i-1].lower()
                    cur_py = py_list[i].lower()
                    py = last_py + ' ' + cur_py
                    if cur_py == '' or last_py == '':
                        continue
                    tmp_dict = {}
                    tmp_w = ''
                    if cur_py not in self.analyzer.single_db.keys():
                        continue
                    for cur in self.analyzer.single_db[cur_py].keys():
                        if cur == '':
                            continue
                        tmp_dict[cur] = {}
                        if last_py not in self.analyzer.single_db.keys():
                            continue
                        for last in self.analyzer.single_db[last_py].keys():
                            tmp_dict[cur][last] = min_num 
                            p = self.trans_pbty(last,cur,last_py,cur_py, py)
                            if i == 1:
                                tmp_dict[cur][last] = p + math.log(self.analyzer.single_db[last_py][last])-math.log(self.analyzer.single_num) 
                            else:
                                for j in self.pb_dict[i-1][last].keys():
                                    f = self.pb_dict[i-1][last][j] + p 
                                    if f > tmp_dict[cur][last]:
                                        tmp_dict[cur][last] = f

                    self.pb_dict[i] = tmp_dict
                ans_list = []
                #self.ans_dict = {}
                if l-1 in self.pb_dict.keys():
                    for cur in self.pb_dict[l-1].keys():
                        ans_list.append(self.find_ans(l-1, cur))
                    ans_nd = node()
                    ans_nd.f = min_num 
                    for item in ans_list:
                        if item.f > ans_nd.f:
                            ans_nd = item
            self.ans_list.append(ans_nd.s) 
            sys.stdout.write('Dealing with...' + str(k) +'/' + str(total)+ '\r')
            k = k + 1
        print()
    def find_ans(self, i, cur):
        if i not in self.ans_dict.keys():
            self.ans_dict[i] = {}
        if cur not in self.ans_dict[i].keys():
            nd = node()
            if i == 0:
                nd.f = 0.0
                nd.s = ''
            else:
                nd.f = min_num 
                for item in self.pb_dict[i][cur].keys():
                    n = self.find_ans(i-1,item)
                    p = self.pb_dict[i][cur][item] + n.f
                    if p > nd.f:
                        nd.f = p
                        if i == 1:
                            nd.s = item + cur
                        else:
                            nd.s = n.s + cur 
            self.ans_dict[i][cur] = nd
        return self.ans_dict[i][cur]
    '''
    def find_ans_1(self, i, cur):
        p = 0.0
        next_w = ''
        for item in self.pb_dict[i][cur].keys():
            if self.pb_dict[i][cur][item] > p:
                p = self.pb_dict[i][cur][item]
                next_w = item 
        return self.find_ans_1(i-1, next_w) + cur
    '''
    def sum(self, word, word_list):
        for item in word_list:
            if item == '':
                continue
            if word == item[0]:
                if len(item) > 1:
                    return item[1]
        return 0
    def trans_pbty(self, last, cur, last_py, cur_py, py):
        cur_cnt = self.analyzer.find_sum(cur, cur_py, 1)
        last_cnt = self.analyzer.find_sum(last, last_py, 1)
        pair_cnt = self.analyzer.find_sum(last+cur, py, 2)
        if last_cnt == 0 or pair_cnt == 0:
            if cur_cnt == 0:
                return math.log(alpha)-math.log(self.analyzer.single_num)
            return math.log(alpha)+math.log(cur_cnt)-math.log(self.analyzer.single_num)
        else:
            return math.log(alpha*(cur_cnt/self.analyzer.single_num) + beta*(pair_cnt / last_cnt)) 
    def write_ans(self, path):
        with open(path, 'w') as f:
            for line in self.ans_list:
                f.write(line + '\n')
    def solve(self, ipt_path, opt_path):
        print('Reading...')
        self.read_in(ipt_path)
        self.viterbi()
        print('Writing...')
        self.write_ans(opt_path)
        print('Done...')
