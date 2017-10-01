import psycopg2

def label_bytime(df):
	"""Shows the user messages from the data frame and prompts the user to label them as spam or non-spame"""
	df = df.sort_values(['time'],ascending=True)
	df.index = range(0,df.shape[0])
	for i in range(0,df.shape[0]):
		if df.loc[i,:]['class']=='none':
			string = df.get_value(i,'edited_message')
			print 'The message is: '+ string
			ruling = raw_input('nothing means spam>>')
			if ruling =='':
				temp = df[df['edited_message']==string]
				temp['class']=0
				df[df['edited_message']==string]=temp
			elif ruling == 'done':
				break
			else:
				temp = df[df['edited_message']==string]
				temp['class']='1'
				df[df['edited_message']==string]=temp
			print 'comments remaining: '+str(df[df['class']=='none'].shape[0])
	print '----------------------------------------------------------------------------------------------------------'
	print '----------------------------------------------------------------------------------------------------------'
	print '----------------------------------------------------------------------------------------------------------'
	print '----------------------------------------------------------------------------------------------------------'
	print '----------------------------------------------------------------------------------------------------------'
	print '----------------------------------------------------------------------------------------------------------'
	file_name = raw_input('file name?>>>')
	df.to_json(file_name)


def add_class(df):
	"""adds a column for class"""
	df['class']=df['spam flag'].apply(lambda x: 1 if x=='non-spam' else 0)
	return df

def label_boarder_case():
	"""Shows the user messages with a certin ratinf from the data frame and prompts the user to label them as spam or non-spame"""
	streamer_name = raw_input('select streamer name>>>>>')
	sql_query ="""
	SELECT * FROM twitch WHERE %s=streamer AND ;
	"""%streamer_name
	df = pd.read_sql_query(sql_query,con)
	df.index = range(0,df.shape[0])
	for i in range(0,df.shape[0]):
		if df.get_value(i,'spam flag')=='none':
			string = df.get_value(i,'edited message')
			print 'The message is: '+ string
			ruling = raw_input('nothing means spam>>')
			if ruling =='':
				temp = df[df['edited message']==string]
				temp['spam flag']='spam'
				df[df['edited message']==string]=temp
			elif ruling == 'done':
				break
			else:
				temp = df[df['edited message']==string]
				temp['spam flag']='non-spam'
				df[df['edited message']==string]=temp
			print 'comments remaining: '+str(df[df['spam flag']=='none'].shape[0])
	print '----------------------------------------------------------------------------------------------------------'
	print '----------------------------------------------------------------------------------------------------------'
	print '----------------------------------------------------------------------------------------------------------'
	print '----------------------------------------------------------------------------------------------------------'
	print '----------------------------------------------------------------------------------------------------------'
	print '----------------------------------------------------------------------------------------------------------'
	file_name = raw_input('file name?>>>')
	df.to_json(file_name)