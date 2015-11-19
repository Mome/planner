from console import getTerminalSize
import box
from copy import copy

bullet_prefix = '-'

def draw_open_table(heads, scedule_times, tasks, consupl):
	assert len(heads)==len(scedule_times)==len(tasks)

	term_width, term_height = getTerminalSize()
	col_num = len(heads)
	colwidth = (term_width+1)//col_num - 1

	horl = consupl.get('top','bot')
	verl = consupl.get('right','left')
	junc = consupl.get('top','bot','right','left')

	columns = copy(heads)

	# add head
	while any(heads):	
		row = [h[:colwidth] for h in heads]
		row = [' ' for cell in row]
		row = verl.join(row)
		table.append(row)
		heads = [h[colwidth:] for h in heads]
	
	# horizontal separation row
	sep = 
	row = sep.join(symboles['horizontal']*(colwidth+2))

	table.append(row)

	# 	

