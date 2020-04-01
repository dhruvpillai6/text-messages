# text-messages

This readme is under construction. Please excuse the brevity.

# Usage

This package is useful for displaying/analyzing text messages with one person and
with everyone that you text. This package only works for people that have text
messages hooked up to iMessages on a Mac.

### To plot your texts with one person:

1. Instantiate a `Conversation` class, providing as an argument a phone number or
Apple ID. Use a `limit=` kwarg to limit the number of SQL results if the queries take
 too long.

2. Use the `.plot_histogram` method to see a full plot of the history of your text
history.

### To plot yours texts with one person in the context of your global texting habits:

1. Instantiate a `AllTexts` object (pass in `limit=` as a kwarg to limit results)

2. Call the `.plot_normalized_histo` method, passing in a phone number or Apple ID
(and an option `limit=`) to see the ratio of your total text messages that are
accounted for by the input contact information.