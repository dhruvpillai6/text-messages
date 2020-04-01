import text_query
import datetime
import matplotlib
import numpy
import pandas
from collections import Counter


class Contact:
    def __init__(self, number, handle_id=None, name=None):
        self.number = number
        self.name = name
        self.handle_id = handle_id

    def __repr__(self):
        return f'<Contact>{self.name}' if self.name else f'<Contact>{self.number} ' \
                                                         f'(handle_id {self.handle_id})'


class TextMessage:
    def __init__(self, timestamp, number, handle_id, content, sent):
        self.timestamp = (datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'))
        self.contact = (Contact(number=number, handle_id=handle_id))
        self.content = content
        self.sent = (bool(sent))

    def __repr__(self):
        action = 'Said' if self.sent else 'Received'
        preposition = 'to' if self.sent else 'from'

        return f'{action} "{self.content}" {preposition} {self.contact} at ' \
               f'{self.timestamp}'


class TextGroup:
    def __init__(self, contacts=None, limit=None):
        self.contacts = []
        all_contacts = text_query.generate_address_book()
        # TODO: Use list comp
        for index, row in all_contacts.iterrows():
            self.contacts.append(Contact(row['id'], index))

        if contacts:
            contacts = self.return_contacts(contacts)[1]

        self.texts = []
        self.dataframe = None
        self.limit = limit
        if contacts is None:
            self.where = [None]
        else:
            self.where = []
            for contact in contacts:
                self.where.append(f'handle_id = {contact.handle_id}')

        dataframes = []
        for where in self.where:
            dataframes.append(text_query.text_query(WHERE=where, LIMIT=self.limit))

        for dataframe in dataframes:
            if self.dataframe is None:
                self.dataframe = dataframe
            else:
                self.dataframe = self.dataframe.append(dataframe)

        for _, row in self.dataframe.iterrows():
            self.texts.append(TextMessage(timestamp=row['local_date'],
                                          number=row['id'],
                                          handle_id=row['handle_id'],
                                          content=row['text'],
                                          sent=row['sent']))
        self.dataframe.loc[:, 'local_date'] = \
            self.dataframe.loc[:, 'local_date'].apply(
                    lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date())

    def return_contacts(self, number):
        contacts = []
        if '+' not in str(number):
            number = f'+1{str(number)}'
        number.replace("-", "")
        returned_contact = []
        for contact in self.contacts:
            if number in contact.number:
                contacts.append(contact)
                returned_contact.append(contact)
        if len(contacts) > 0:
            return contacts, returned_contact

        raise ValueError(f'The entered phone number {number} is not in the database')

    def generate_histogram(self, dataframe, moving_average_window=None):
        dataframe.drop(columns=['handle_id', 'id'], inplace=True)
        dataframe.rename(columns={'text': 'total'}, inplace=True)
        dataframe.loc[:, 'sent'] = \
            dataframe['sent'].apply(lambda x: numpy.nan if x == 0 else x)
        dataframe = dataframe.groupby(dataframe.local_date).count()
        dataframe['received'] = dataframe['total'] - dataframe['sent']
        date_range = pandas.date_range(dataframe.index.min(), dataframe.index.max())
        dataframe = dataframe.reindex(date_range, fill_value=0)

        if moving_average_window:
            if not isinstance(moving_average_window, int):
                raise TypeError(f'Your moving average input was {moving_average_window}'
                                f' and needs to be of type int')
            dataframe = dataframe.rolling(window=moving_average_window).mean()

        return dataframe

    def filter_by_content(self, *args, moving_average_window=None, dataframe=None):
        """
        Usage: Use to plot a histogram of texts exchanged in a conversation and
        filtering by the keywords provided in ags.
        :param args: Words that must be in the text messages. Entered as separate
        arguments. All words should be entered as strings. Enforces a logical
        'and'--will only return text messages that contain all of the words,
        is unable to do 'or'.
        :param moving_average_window: an int, in days, that should be used to obtain
        a moving average
        :param dataframe: a pandas DataFrame containing text message data
        :return: pandas DataFrame containing the number of filtered text messages,
        binned by date.
        """
        # TODO: Handle args that are ints but should be strings
        # TODO: Provide a help function explaining parameters
        # TODO: Handle 'or'--curently just works for 'and'
        # TODO: Cleanse the inputs from the user--cast args to str
        # TODO: Handle empty args
        if dataframe is None:
            dataframe = self.dataframe
        elif not isinstance(dataframe, pandas.DataFrame):
            raise TypeError(f'Expected input dataframe, instead got {type(dataframe)}')
        for arg in args:
            if isinstance(arg, tuple):
                for item in arg:
                    dataframe = \
                        dataframe[dataframe['text'].str.lower().str.contains(item)]
        dataframe = self.generate_histogram(dataframe, moving_average_window)
        return dataframe

    def most_frequent_words(self, dataframe=None, lowest_rank=10):
        """
        Takes in a pandas DataFrame of text messages and outputs the most frequently
        used words in that set of text messages.
        :param dataframe: a pandas DataFrame of text messages, which will be the
        source of the text messages that will be counted
        :param lowest_rank: The lowest rank that will be output by the method. By
        default the method will output the top 10 words.
        :return: pandas.DataFrame with common words and the frequency with which they
        are seen in text messages
        """
        if not dataframe:
            dataframe = self.dataframe
        print(dataframe)
        lists_of_texts = dataframe["text"].str.lower().str.split().tolist()
        master_list = []
        for list in lists_of_texts:
            # Handle the case where the text message is empty, like a person sending
            # a picture
            if list is None:
                continue
            for item in list:
                master_list.append(item)

        world_count_tups = Counter(master_list).most_common(lowest_rank)
        word_count = []
        for tup in world_count_tups:
            word_count.append((tup[0], round(tup[1]/len(master_list), 3)))

        return pandas.DataFrame(word_count)


class Conversation(TextGroup):
    def __init__(self, handle_id=None, limit=None):
        super().__init__(handle_id, limit)

        self.contact = self.texts[0].contact

    def __repr__(self):
        return_string = f'Conversation with {self.contact}'
        return_string2 = ''.join(f'{self.texts[i]} \n' for i in range(0, 5))
        return f'\n{return_string}\n\n{return_string2}'

    def __len__(self):
        return len(self.texts)

    def plot_histogram(self, dataframe=None, moving_average_window=None):
        dataframe = self.dataframe.copy() if not dataframe else dataframe
        self.generate_histogram(dataframe, moving_average_window).plot(
                title=f'Total Text Messages with {self.contact}')
        matplotlib.pyplot.show()

    def plot_filtered_histogram(self, *args, moving_average_window=None):
        self.filter_by_content(moving_average_window, args).plot()
        matplotlib.pyplot.show(title=f'Total Text Messages with {contact}')


class AllTexts(TextGroup):
    def __init__(self, handle_id=None, limit=None):
        super().__init__(handle_id, limit)

    def normalized_histogram(self, contact, moving_average_window=None, limit=None):
        if not isinstance(contact, Contact):
            contacts = self.return_contacts(contact)
        conversation = Conversation(contacts[0], limit)
        all_texts_histo = self.generate_histogram(self.dataframe,
                                                  moving_average_window)

        contact_histo = self.generate_histogram(conversation.dataframe,
                                                moving_average_window)
        min_date = max(all_texts_histo.index.min(), contact_histo.index.min())
        all_texts_histo = all_texts_histo.drop([date for date in all_texts_histo.index
                                                if date < min_date])
        contact_histo = contact_histo.drop([date for date in contact_histo.index
                                                if date < min_date])
        contact_histo['total_ratio'] = contact_histo['total'] / all_texts_histo['total']
        contact_histo['sent_ratio'] = contact_histo['sent'] / all_texts_histo['sent']
        contact_histo['received_ratio'] = \
            contact_histo['received'] / all_texts_histo['received']

        contact_histo.drop(columns=['total', 'received', 'sent'],
                           inplace=True)
        return contact_histo

    def plot_normalized_histo(self, contact, dataframe=None,
                              moving_average_window=None, limit=None):
        if dataframe is None:
            dataframe = self.normalized_histogram(contact, moving_average_window, limit)
        contact = self.return_contacts(contact)[1][0]
        dataframe.plot(title=f'Text Message Ratio with {contact}')
        matplotlib.pyplot.show()


if __name__ == '__main__':
    pass
