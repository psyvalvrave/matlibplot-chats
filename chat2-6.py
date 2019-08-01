# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 12:25:47 2019

@author: Zhecheng
"""
#need to save the fig
import pandas as pd
import matplotlib.pyplot as plt

DIRECTORY_PATH="../traders/"
CSV_DISCUSSION_POSTS="discussion_posts.tsv"
CSV_DISCUSSIONS="discussions.tsv"
CSV_MESSAGES="messages.tsv"
CSV_USERS="users.tsv"
MILESECOND_TO_DAYS=8.64*10**7

def coverter(n):
    return n/MILESECOND_TO_DAYS

file_users = pd.read_csv(DIRECTORY_PATH+CSV_USERS,delimiter='\t').set_index('id')
file_discussions = pd.read_csv(DIRECTORY_PATH+CSV_DISCUSSIONS,delimiter='\t')
file_messages = pd.read_csv(DIRECTORY_PATH+CSV_MESSAGES,delimiter='\t')
file_discussion_posts = pd.read_csv(DIRECTORY_PATH+CSV_DISCUSSION_POSTS,delimiter='\t')

#Part 1

print("How many users are in the database?")
print(file_users.size)

print("What is the time span of the database?")
time = pd.concat([file_users['memberSince'], file_discussions['createDate'], 
                    file_messages['sendDate'], file_discussion_posts['createDate']])
print(coverter(time.max()-time.min()))

print("How many messages of each type have been sent?")
plt.figure(1,figsize=(10,10))
plt.title('Type of Messages')
count_messages_type = file_messages.groupby("type").count().id
autopct1=lambda x: str(int(round(x*sum(count_messages_type.iloc[0:])/100)))+"("+'%.2f'%x+"%)"
messages_pie = plt.pie(count_messages_type.iloc[0:],labels=count_messages_type.index,autopct=autopct1)
plt.savefig('Type of Messages')
plt.close()


print("How many discussions of each type have been started?")
plt.figure(2,figsize=(10,10))
plt.title('Categories of Discussions')
count_discussionsCategory = file_discussions.groupby("discussionCategory").count().id
autopct2=lambda x: str(int(round(x*sum(count_discussionsCategory.iloc[0:])/100)))+"("+'%.2f'%x+"%)"
discussions_pie = plt.pie(count_discussionsCategory.iloc[0:],labels=count_discussionsCategory.index,autopct=autopct2)  
plt.savefig('Categories of Discussions')
plt.close()

print('How many discussion posts have been posted?')
print(file_discussion_posts.id.size)

#Part 2

messages = file_messages.set_index('sender_id').drop(['id', 'type'], axis=1)
max_d = messages.groupby('sender_id').max()
min_d = messages.groupby('sender_id').min()
activity_ranges = coverter(max_d.sub(min_d))
plt.figure(3,figsize=(10,10))
plt.title('Activity Range Distribution')
plt.hist(activity_ranges.values, bins=20, log=True, alpha=0.5)
plt.savefig('Activity Range Distribution')
plt.close()
activity_range=activity_ranges.iloc[:,0]
#Part 3

messages = file_messages.set_index('sender_id').drop(columns='id')
m = messages.join(file_users, how='inner')
m.index.name = 'id'
m = m.groupby(['id', 'type']).min()
ma = coverter(m.sendDate.sub(m.memberSince))
ma = ma.reset_index().set_index('id')
ma.columns=['type', 'delay']
mc = ma.groupby('type')
plt.figure(4,figsize=(10,10))
plt.title('Message Activity Delay Distribution')
for i,a in mc:
    md = a.drop(columns='type').values
    plt.hist(md, bins=20, log=True, alpha=0.5, label=i)
plt.legend(loc='best')
plt.savefig('Message Activity Delay Distribution')
plt.close()   

#Part 4
count_category = file_discussions.groupby("discussionCategory").count().id.sort_values(ascending=False)
autopct3=lambda x:str(int(round(x*sum(count_category.iloc[0:])/100)))+"("+'%.2f'%x+"%)"
explode = [0]*count_category.size
explode[0] = 0.1
plt.figure(5,figsize=(10,10))
plt.title("Majority of Discussion Categories")
category_pie = plt.pie(count_category.iloc[0:],labels=count_category.index,
                       autopct=autopct3,explode=explode,shadow=True)
plt.savefig("Majority of Discussion Categories")
plt.close()

#Part 5
most_popular = count_category.index[0]
diss_m = file_discussions.set_index('id').drop(['createDate', 'creator_id'], axis=1)
diss_m = diss_m[diss_m.discussionCategory==most_popular]
post_m = file_discussion_posts.set_index('discussion_id').drop(columns='id')
diss_post = post_m.join(diss_m, how='inner').set_index('creator_id').drop('discussionCategory', axis=1)
diss_post = diss_post.groupby('creator_id').min()
post_user = diss_post.join(file_users, how='inner')
post_user.index.name = 'user_id'
post_user.columns=['postDate', 'userCreateDate']
post_delays = coverter(post_user.postDate.sub(post_user.userCreateDate))
plt.figure(6,figsize=(10,10))
plt.title('Post Activity Delays Distribution')
plt.hist(post_delays.values, bins=20, log=True, alpha=0.5)
plt.savefig('Post Activity Delays Distribution')
plt.close()

#Part 6
file_user = file_users
file_user.index.names = ['sender_id']
file_messages_delay = file_user.join(file_messages.set_index('sender_id')).drop(columns='id')
friend_link_request = file_messages_delay[file_messages_delay.type=='FRIEND_LINK_REQUEST']
friend_link_request_sent = friend_link_request.drop(columns='memberSince').groupby('sender_id').min()
direct_message = file_messages_delay[file_messages_delay.type=='DIRECT_MESSAGE']
direct_message_sent = direct_message.drop(columns='memberSince').groupby('sender_id').min()
messages_delay_friend = coverter(friend_link_request_sent.loc[:,'sendDate']-file_messages_delay.memberSince).dropna().drop_duplicates()
messages_delay_direct = coverter(direct_message_sent.loc[:,'sendDate']-file_messages_delay.memberSince).dropna().drop_duplicates()

plt.figure(7,figsize=(10,10))
plt.title('Box Plot of Distributions')
plt.subplot(1, 4, 1)
plt.title('Friend Request')
messages_delay_friend.plot.box(label="").set_ylabel("Box plot")
plt.yscale('log')

plt.subplot(1, 4, 2)
plt.title('Direct Message')
messages_delay_direct.plot.box(label="")
plt.yscale('log')

plt.subplot(1, 4, 3)
plt.title('Activity Delay')
post_delays.plot.box(label="")
plt.yscale('log')

plt.subplot(1, 4, 4)
plt.title('Activity Range')
activity_range.plot.box(label="")
plt.yscale('log')

plt.savefig('Box Plot of Distributions')
plt.close()