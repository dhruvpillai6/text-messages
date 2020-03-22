import text_query
import datetime
import matplotlib
import numpy

class Contact:
    def __init__(self, number, name=None):
        self.number = (number)
        self.name = (name)

    def __repr__(self):
        return f'{self.name}' if self.name else f'{self.number}'

class TextMessage:
    def __init__(self, timestamp, number, content, sent):
        self.timestamp = (datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'))
        self.contact = (Contact(number=number))
        self.content = (content)
        self.sent = (bool(sent))

    def __repr__(self):
        action = 'Said' if self.sent else 'Received'
        preposition = 'to' if self.sent else 'from'

        return f'{action} "{self.content}" {preposition} {self.contact} at ' \
               f'{self.timestamp}'

class Conversation:
    def __init__(self, handle_id, limit):
        self.texts = []
        self.dataframe = text_query.text_query(WHERE=f'handle_id = {handle_id}')

        for _, row in self.dataframe.iterrows():
            self.texts.append(TextMessage(timestamp=row['local_date'],
                                          number=row['id'],
                                          content=row['text'],
                                          sent=row['sent']))

        self.contact = self.texts[0].contact

    def __repr__(self):
        return_string = f'Conversation with {self.contact}'
        return_string2 = ''.join(f'{self.texts[i]} \n' for i in range(0, 5))
        return f'\n{return_string}\n\n{return_string2}'

    def __len__(self):
        return len(self.texts)

    def histogram(self):
        self.dataframe['local_date'] = \
            self.dataframe['local_date'].apply(
                    lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date())
        self.dataframe.drop(columns=['handle_id', 'id'], inplace=True)
        self.dataframe.rename(columns={'text':'total'}, inplace=True)
        self.dataframe['sent'] = \
            self.dataframe['sent'].apply(lambda x: numpy.nan if x == 0 else x)
        self.dataframe = self.dataframe.groupby(self.dataframe.local_date).count()
        self.dataframe['received'] = self.dataframe['total'] - self.dataframe['sent']
        print(self.dataframe)
        self.dataframe.plot()
        matplotlib.pyplot.show()

if __name__ == '__main__':
    pranav = Conversation(6, 10)
    pranav.histogram()