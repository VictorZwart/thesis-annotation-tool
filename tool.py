# Thesis Annotation Tool
# version 2.1
# by Robin van der Noord, s3745686
# Python 3.8 or better
import sys
import re
import csv

ENCODING = 'UTF-8'


class Tool:
    EXPLICITNESS = {
        'e': 'EXPLICIT',
        'i': 'IMPLICIT',
        'n': 'NOT',
    }
    TARGET = {
        'i': 'INDIVIDUAL',
        'g': 'GROUP',
        'o': 'OTHER',
        'n': 'NOT',
    }

    def __init__(self, input_file, output_file=None):
        self.output_file = output_file or input_file

        username_re = re.compile(r'@(\w){1,15}')
        url_re = re.compile(r'https?://t.co/\w+')

        self.history = {}
        self.todo = []

        with open(input_file, encoding=ENCODING) as f:
            reader = csv.DictReader(f, delimiter='\t')

            # build history of scores:
            for line in reader:
                line['stripped'] = re.sub(url_re, 'http://_', re.sub(username_re, '@_', line['text']))
                if line.get('explicitness') and not self.history.get(line['stripped']):
                    self.history[line['stripped']] = (line['explicitness'], line.get('target'))
                self.todo.append(line)

    def save(self):
        print('saving')

        with open(self.output_file, 'w', newline='', encoding=ENCODING) as csvfile:
            fieldnames = ['id', 'text', 'user', 'source', 'user.description', 'split', 'explicitness', 'target']
            writer = csv.DictWriter(csvfile,
                                    fieldnames=fieldnames,
                                    delimiter='\t',
                                    extrasaction='ignore'  # <- ignore 'stripped'
                                    )
            writer.writeheader()
            writer.writerows(self.todo)
        print('done!')
        exit()

    def annotate_tweet(self, index, tweet):
        explicitness_score = None
        target_score = None

        print(f"{index + 1}/{len(self.todo)}")
        print(tweet['text'])
        if (explicitness_score := tweet.get('explicitness')) \
                and (target_score := tweet.get('target')) \
                or (explicitness_score == 'NOT'):
            # old tweet
            print(f'Tweet already annotated with {explicitness_score} {f"and {target_score}" if target_score else ""}')
            return

        if scores := self.history.get(tweet.get('stripped')):
            # similar tweet
            explicitness_score, target_score = scores
            print(f'Similar Tweet annotated with {explicitness_score} {f"and {target_score}" if target_score else ""}')
        else:
            # new tweet
            while True:
                explicitness_choice = (
                        input('EXPLICITNESS: [E]XPLICIT | [I]MPLICIT | [N]OT | [S]TOP ? ') + ' '  # <- ' ' prevents err
                )[0].lower()  # grab first letter

                if explicitness_choice in self.EXPLICITNESS.keys():
                    explicitness_score = self.EXPLICITNESS[explicitness_choice]
                    break
                elif explicitness_choice == 's':
                    self.save()

            if explicitness_score != 'NOT':
                while True:
                    target_choice = (
                            input('TARGET: [I]NDIVIDUAL | [G]ROUP | [O]THER | [N]ONE | [S]TOP ? ') + ' '
                    # ' ' prevents error
                    )[0].lower()
                    if target_choice in self.TARGET.keys():
                        target_score = self.TARGET[target_choice]
                        break
                    elif target_choice == 's':
                        self.save()
            else:
                target_score = None

        tweet['explicitness'] = explicitness_score
        tweet['target'] = target_score

    def main(self):
        for (index, tweet) in enumerate(self.todo):
            try:
                self.annotate_tweet(index, tweet)
            except Exception as e:
                print('### Err:')
                print(e)
                print(index, tweet)
                self.save()

        # all done!
        self.save()


if __name__ == '__main__':
    t = Tool(*sys.argv[1:])
    t.main()
    # usage: python tool.py <input file> [output file]
