import text_query
import datetime
import matplotlib
import numpy


class Contact:
    def __init__(self, number, name=None):
        self.number = number
        self.name = name

    def __repr__(self):
        return f'{self.name}' if self.name else f'{self.number}'


class TextMessage:
    def __init__(self, timestamp, number, content, sent):
        self.timestamp = (datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'))
        self.contact = (Contact(number=number))
        self.content = content
        self.sent = (bool(sent))

    def __repr__(self):
        action = 'Said' if self.sent else 'Received'
        preposition = 'to' if self.sent else 'from'

        return f'{action} "{self.content}" {preposition} {self.contact} at ' \
               f'{self.timestamp}'


class Conversation:
    def __init__(self, handle_id, limit=None):
        self.texts = []
        self.dataframe = text_query.text_query(WHERE=f'handle_id = {handle_id}',
                                               LIMIT=limit)

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

    def generate_histogram(self, dataframe, moving_average_window=None):
        dataframe.loc[:, 'local_date'] = \
            dataframe.loc[:, 'local_date'].apply(
                    lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date())
        dataframe.drop(columns=['handle_id', 'id'], inplace=True)
        dataframe.rename(columns={'text': 'total'}, inplace=True)
        dataframe.loc[:, 'sent'] = \
            dataframe['sent'].apply(lambda x: numpy.nan if x == 0 else x)
        dataframe = dataframe.groupby(dataframe.local_date).count()
        dataframe['received'] = dataframe['total'] - dataframe['sent']

        if moving_average_window:
            if not isinstance(moving_average_window, int):
                raise TypeError(f'Your moving average input was {moving_average_window}'
                                f' and needs to be of type int')
            dataframe = dataframe.rolling(window=moving_average_window).mean()

        return dataframe

    def plot_histogram(self, moving_average_window=None):
        self.generate_histogram(self.dataframe, moving_average_window).plot()
        matplotlib.pyplot.show()

    def filter_by_content(self, *args, moving_average_window=None):
        dataframe = self.dataframe
        for arg in args:
            if isinstance(arg, tuple):
                for item in arg:
                    dataframe = \
                        dataframe[dataframe['text'].str.lower().str.contains(item)]
        dataframe = self.generate_histogram(dataframe, moving_average_window)
        return dataframe

    def plot_filtered_histogram(self, *args, moving_average_window=None):
        self.filter_by_content(moving_average_window, args).plot()
        matplotlib.pyplot.show()

if __name__ == '__main__':
    pranav = Conversation(6)
    pranav.plot_filtered_histogram('rip')
    print(pranav)
