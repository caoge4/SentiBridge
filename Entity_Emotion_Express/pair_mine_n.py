# coding=utf8
from __future__ import division
import gensim

class pair_mine():

    def __init__(self, args):
        # self.new_model = gensim.models.Word2Vec.load(args.word2vec)
        self.new_model = gensim.models.KeyedVectors.load_word2vec_format(args.word2vec, binary=False)
        self.pair_mine_score = {}
        self.pair_mine_count = {}
        count = 0
        pair_useful = {}
        pair_useless = {}
        fp = open(args.read_path, 'rb')
        for line in fp:
            count += 1
        base_line = args.split_point * count
        # dead_line = 0.3*count
        print base_line
        fp.seek(0)

        count = 0
        for line in fp:
            n,s,score = line.strip().split('\t')
            if count > base_line:
                if n not in pair_useless:
                    pair_useless[n] = {}
                    pair_useless[n][s] = score
                elif s not in pair_useless[n]:
                    pair_useless[n][s] = score
            elif count < base_line:
                if n not in pair_useful:
                    pair_useful[n] = {}
                    pair_useful[n][s] = score
                elif s not in pair_useful[n]:
                    pair_useful[n][s] = score
            count += 1
        self.pair_useful = pair_useful
        self.pair_useless = pair_useless
        # print self.pair_useful
        # print self.pair_useless
        count = 0
        # 挖矿2.0开始
        for n in pair_useless:
            #  print(count)
            # 情感词候选区
            # print n
            s_renew = {}
            if n in pair_useful:
                for word in pair_useful[n]:
                    s_renew[word] = 0.0
            for s in pair_useless[n]:
                # print s
                for sim_s in s_renew:
                    # print sim_s, s
                    # print self.new_model[s]
                    # print self.new_model[sim_s]
                    try:
                        # print self.new_model[s]
                        # print self.new_model[sim_s]
                        s_renew[sim_s] = float(self.new_model.similarity(s.decode('utf8'), sim_s.decode('utf8')))
                        # print s_renew[sim_s]
                    except KeyError:
                        # print '111'
                        pass
                sum = 0
                for sim_s in s_renew:
                    sum += s_renew[sim_s]
                numb = len(s_renew)
                if numb:
                    score = sum / len(s_renew)
                else:
                    score = 0.0
                self.pair_mine_score[n + '\t' + s] = score
                self.pair_mine_count[n + '\t' + s] = numb
            count += 1
        self.pair_mine_sort = sorted(self.pair_mine_score.iteritems(), key=lambda d:d[1], reverse = True)
        # 挖矿2.0结束

    def write(self, path):
        f = open(path, 'wb')
        for _ in self.pair_mine_sort:
            f.write(_[0] + '\t' + str(_[1]) + '\t' + str(self.pair_mine_count[_[0]]) + '\n')

    def sent_del(self, sent_renew):
        if '好' in sent_renew:
            del sent_renew['好']

def main():
    import argparse
    parser = argparse.ArgumentParser(description='build candidate set')
    parser.add_argument('--read_path', default='./CCF_data/Iterative_record/pair_sort_ns/99', help='file path')
    parser.add_argument('--split_point', type=float, default=0.1, help='split point [pair_useful, pair_useless]')
    parser.add_argument('--word2vec', default='./CCF_data/word2vec.model.txt', help='word2vec path')
    parser.add_argument('--result_path', default='./CCF_data/pair_mine_n_result', help='file path')
    args = parser.parse_args()
    p = pair_mine(args)
    p.write(args.result_path)

if __name__ == '__main__':
    main()
