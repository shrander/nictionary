import sys
import time

class sentence:
    def __init__(self, sentence=''):
        self.sent=sentence
        self.list=sentence.split()
        self.pos={}
    
    def tag_sentence(self, lexicon):
        for each in self.list:
            try:
                self.pos[each] = lexicon[each]
            except KeyError as e:
                print e
                raise KeyboardInterrupt

    def _get_object_string(self):
        return self.sent
        
    def __unicode__(self):
        return self._get_object_string()
        
    def __str__(self):
        return unicode(self).encode('utf-8')
                
class chart:
    def __init__(self,sent):
        self.dot=0
        self.sentence=sentence(sent)
        self.tree=[]
    
    def next_cat(self, rule, idx, pos):
        try:
            if rule.list[self.dot+1] in pos:
                return True
            return False
        except:
            return False
    
    def get_word(self, idx):
        return self.sentence.list[idx]
        
    def get_pos(self, idx):
        return self.sentence.pos[self.get_word(idx)]
    
    def enqueue(self, state, idx):
        try:
            if state not in self.tree[idx]:
                self.tree[idx].append(state)
        except IndexError:
            self.tree.append([])
            self.tree[idx].append(state)
            
    def incomplete(self, rule):
        if self.dot < len(rule.list[1:]) and self.dot != len(self.sentence.list):
            return True
        return False
    
    def print_tree(self,i):
        print "Chart["+str(i)+']'
        for each in self.tree[i]:
            print ' '+ str(each)
        
    def get_states(self, idx):
        return self.tree[idx]
    
    def _get_object_string(self):
        return str(self.sentence)
        
    def __unicode__(self):
        return self._get_object_string()
        
    def __str__(self):
        return unicode(self).encode('utf-8')
                
class grammar:
    def __init__(self):
        self.rules = []
    
    def init_rules(self,file_name):
        fh=open(file_name)
        for each_line in fh.readlines():
            if each_line.lower().rstrip() == '':
                continue
            self.rules.append(grammar_rule(each_line.lower().rstrip()))

    def grammar_rules_for(B):
        sub_list = []
        for each in self.rules:
            if each.list[0] == B:
                sub_list.append(each)
        return sub_list
        
    def _get_object_string(self):
        blob=''
        for each in self.rules:
            blob += str(each)
        return blob
        
    def __unicode__(self):
        return self._get_object_string()
        
    def __str__(self):
        return unicode(self).encode('utf-8')
                
class grammar_rule:
    def __init__(self, raw, pos=0, dot=0):
        """
        raw - grammar encoded as text string
        """
        self.list=raw.split()
        self.pos = pos
        self.dot = dot
            
    def _get_object_string(self):
        i = iter(self.list)
        blob = i.next()+' -> ' 
        for each in i:
            blob += each+' '
        return blob
    
    def __unicode__(self):
        return self._get_object_string()
        
    def __str__(self):
        return unicode(self).encode('utf-8')
    

class nictionary:
    def __init__(self):
        self.args={}
        self.in_file=''
        self.pos=[]
        self.lexicon = {}
        self.grammar=grammar()
        self.charts=[] # list of charts
        
    def usage(self):
        print 'USAGE: nictionary.py [options] [input_file]'
        print ' [input_file]    file will contain noun phrases that will be parsed'
        print ' -h              prints out this help'
        print '\n'
        sys.exit(0)
        
    def parse_args(self, args):
        i=0
        if len(args)<=1:
            self.usage()
        while(i<len(args)):
            if args[i][0]== '-':
                if args[i]=='-h':
                    self.usage()
                else:
                    self.usage()
            else:
                self.in_file = args[i]
            i+=1
        
    def init_data(self):
        try:
            # init parts of speech types from file
            hndl = open('pos','r')
            for each in hndl.readlines():
                if each.lower().rstrip() not in self.pos:
                    self.pos.append(each.lower().rstrip())
            hndl.close()
            
            # init the lexicon from file
            hndl = open('lexicon', 'r')
            for each in hndl.readlines():
                self.lexicon[each.lower().split()[0]]=each.split()[1]
            hndl.close()
            
            #init grammar rules object
            self.grammar.init_rules('grammar')
            
            # build handler for input file
            hndl = open(self.in_file, 'r')
            for each in hndl.readlines():
                if each.strip()=='':
                    continue
                self.charts.append(chart(each.rstrip()))
            for each in self.charts:
                each.sentence.tag_sentence(self.lexicon)
            hndl.close()
        except IOError as e:
            print 'could not open file'
            print e
           
    def earley_parse(self, chart, grammar):
        i=0
        chart.enqueue(grammar_rule('A s'),chart.dot)
        while(i<len(chart.sentence.sent)):
            print 'i '+str(i)
            for each in chart.get_states(i):
                if chart.incomplete(each) and not chart.next_cat(each, i, self.pos):
                    self.predictor(chart, each)
                elif chart.incomplete(each) and chart.next_cat(each, i, self.pos):
                    self.scanner(chart,each,i)
                else:
                    i+=self.completer(chart,each,i)
                    #chart.print_tree(i)

    def predictor(self, chart, rule):
        for each in self.grammar.rules:   
            if each.list[0] == rule.list[chart.dot+1] and each not in chart.get_states(chart.dot):
                each.pos = chart.dot
                each.dot = chart.dot
                chart.enqueue(each, chart.dot)
                print '%-17s (%d,%d) predictor' % (str(each),each.pos,each.dot)

    def scanner(self, chart, rule, i):
        temp = chart.get_pos(chart.dot)
        if 'n' == chart.get_pos(chart.dot)[0] or 'v' == chart.get_pos(chart.dot)[0]:
            temp = chart.get_pos(chart.dot)[0]
        if rule.list[chart.dot+1].strip() == temp:
            r = grammar_rule(rule.list[chart.dot+1]+' '+chart.get_word(chart.dot),i,chart.dot+1)
            chart.enqueue(r, i+1)
            chart.dot = i+1
            print '%-17s (%d,%d) scanner'% (str(r),r.pos,r.dot)
        
    def completer(self, chart, rule,i):
        print
        for each in chart.get_states(rule.pos):
            if rule.list[-1] in each.list[1:]:
                print '%-17s (%d,%d) completer' % (str(each),each.pos,each.dot)
                each.dot=chart.dot
                chart.enqueue(each, chart.dot)
        return 1

    def main(self, args):
        self.parse_args(args)
        self.init_data()
        for each in self.charts:
            print 'Parsing:'
            print each
            self.earley_parse(each, self.grammar)
            i=0
            while(i<=each.dot):
                each.print_tree(i)
                i+=1
        return
        
if __name__ == '__main__':
    try:
        a = nictionary()
        a.main(sys.argv)
    except KeyboardInterrupt as e:
        print e