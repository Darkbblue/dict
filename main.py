import csv
import sys
import json
import random


# 单词池参数，生成单词表时从每个池子取多少单词
num_from_unviewed = 10  # 尚未看过
num_from_to_review = 10  # 待复习 (看到后感觉记不住，需要之后复习)
num_from_learnt = 3  # 已经记住
# 来源词库，使用前修改，文件名不含 .json 扩展名
dict_source = ['CET6_3']


def init():
	'''
	仅运行一次
	'''
	original_dict = {}
	unviewed_dict = {}
	for s in dict_source:
		with open('selected/'+s+'.json', 'r') as f:
			for word in f.readlines():
				data = json.loads(word)
				key = s + '_' + data['headWord']
				original_dict[key] = data
				unviewed_dict[key] = 1

	print(len(original_dict))
	with open('selected/original_dict.json', 'w') as f:
		f.write(json.dumps(original_dict))
	with open('active/unviewed_dict.json', 'w') as f:
		f.write(json.dumps(unviewed_dict))
	with open('active/learnt_dict.json', 'w') as f:
		f.write(json.dumps({}))
	with open('active/to_review_dict.json', 'w') as f:
		f.write(json.dumps({}))


def get_random_list_from_candidates(candidates, count):
	'''
	从候选列表 candidates 中随机取出无重的 count 个元素，若候选项不足该数目，则全部取出
	:param candidates: list
	:param count: int
	:return: list
	'''
	random.shuffle(candidates)
	return candidates[: count]


def generate_word_info(word):
	info = ''
	content = word['content']['word']['content']

	# 核心单词
	info += word['headWord'] + '\n'

	# 发音
	info += '发音\n'
	prefix = '\t'
	if 'usphone' in content:
		info += prefix + 'us: ' + content['usphone']
	if 'ukphone' in content:
		info += prefix + 'uk: ' + content['ukphone']
	info += '\n'

	# 释义
	info += '释义\n'
	prefix = '\t'
	for entry in content['trans']:
		info += prefix + entry['pos'] + ' '
		info += entry['tranCn'] + '\n'
		if 'tranOther' in entry:
			info += prefix + entry['tranOther'] + '\n'
		info += '\n'

	# 词根记忆
	if 'remMethod' in content:
		info += '记忆\n'
		prefix = '\t'
		info += prefix + content['remMethod']['val'] + '\n'

	# 短语
	if 'phrase' in content:
		info += '短语\n'
		prefix = '\t'
		for entry in content['phrase']['phrases']:
			info += prefix + entry['pContent'] + ' '
			info += entry['pCn'] + '\n'

	# 真题例句
	if 'realExamSentence' in content:
		info += '真题例句\n'
		prefix = '\t'
		for entry in content['realExamSentence']['sentences']:
			info += prefix + entry['sContent'] + '\n'

	# 例句
	if 'sentence' in content:
		info += '例句\n'
		prefix = '\t'
		for entry in content['sentence']['sentences']:
			info += prefix + entry['sContent'] + '\n'
			info += prefix + entry['sCn'] + '\n'
			info += '\n'

	info += '\n--------------------------\n\n'

	return info


# 获取词典信息
with open('selected/original_dict.json', 'r') as f:
	original_dict = json.load(f)
with open('active/unviewed_dict.json', 'r') as f:
	unviewed_dict = json.load(f)
with open('active/learnt_dict.json', 'r') as f:
	learnt_dict = json.load(f)
with open('active/to_review_dict.json', 'r') as f:
	to_review_dict = json.load(f)


if len(sys.argv) != 2:
	exit(0)


if sys.argv[1] == 'init':
	init()


if sys.argv[1] == 'get':

	# 获取单词表

	word_sheet = ''  # 完整的单词信息
	feed_back = ''  # 回执，提供单词去向
	ref = ''  # 回执参考，包含完整的 key 表达，但是可读性较差

	# 获取单词列表
	words = []
	words += get_random_list_from_candidates(list(unviewed_dict.keys()), num_from_unviewed)
	words += get_random_list_from_candidates(list(to_review_dict.keys()), num_from_to_review)
	words += get_random_list_from_candidates(list(learnt_dict.keys()), num_from_learnt)

	# 生成单词表和绘制
	for word in words:
		word_sheet += generate_word_info(original_dict[word])
		feed_back += original_dict[word]['headWord'] + ',\n'
		ref += word + '\n'

	# 写入文件
	with open('word_sheet/word_sheet', 'w') as f:
		f.write(word_sheet)
	with open('word_sheet/feed_back', 'w') as f:
		f.write(feed_back)
	with open('active/.ref', 'w') as f:
		f.write(ref)


if sys.argv[1] == 'set':

	# 修改单词池

	with open('word_sheet/feed_back', 'r') as f_feed_back:
		with open('active/.ref', 'r') as f_ref:
			feed_back = csv.reader(f_feed_back)
			ref = csv.reader(f_ref)
			for line, keys in zip(feed_back, ref):
				word = keys[0]

				# 删除已有记录
				if word in unviewed_dict:
					del unviewed_dict[word]
				if word in to_review_dict:
					del to_review_dict[word]
				if word in learnt_dict:
					del learnt_dict[word]

				# 根据用户选项放入已学会池或待复习池
				if line[1] == '1':
					learnt_dict[word] = 1
				else:
					to_review_dict[word] = 1

	# 保存记录
	with open('active/unviewed_dict.json', 'w') as f:
		f.write(json.dumps(unviewed_dict))
	with open('active/learnt_dict.json', 'w') as f:
		f.write(json.dumps(learnt_dict))
	with open('active/to_review_dict.json', 'w') as f:
		f.write(json.dumps(to_review_dict))
