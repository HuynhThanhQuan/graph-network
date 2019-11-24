import numpy as np
import logging
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import matplotlib.colors as mcolors
import mpld3
from matplotlib.patches import Rectangle
from mpld3._server import serve
import os
import gensim
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DEFAULT_LOCATION = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'word2vec_model', 'default_model.w2v')


class Word2VectorManagement:
    def __init__(self, sentences=None, location=DEFAULT_LOCATION, overlapped=False):
        self.sentences = sentences
        self.overlapped = overlapped
        self.gensim_word2vec = None
        self.non_overlapped_sentences = None
        self.load_pretrained_model(location)

    def load_pretrained_model(self, location):
        if os.path.exists(location):
            logger.info('Load pretrained Word2Vector at {}'.format(location))
            self.gensim_word2vec = gensim.models.Word2Vec.load(DEFAULT_LOCATION)
            if self.overlapped is True:
                logger.warning('Accepting pretrained sentences - NOT REFLECTING DATA-DRIVEN ITSELF')
                self.gensim_word2vec.build_vocab(self.sentences, update=True)
                self.gensim_word2vec.train(self.sentences,
                                           total_examples=self.gensim_word2vec.corpus_count,
                                           epochs=self.gensim_word2vec.iter)
            else:
                self.non_overlapped_sentences = self.filter_overlapped_sentences()
                if len(self.non_overlapped_sentences):
                    start = datetime.now()
                    self.gensim_word2vec.build_vocab(self.non_overlapped_sentences, update=True)
                    self.gensim_word2vec.train(self.sentences,
                                               total_examples=self.gensim_word2vec.corpus_count,
                                               epochs=self.gensim_word2vec.iter)
                    logger.info('Training on new sentences {}'.format(datetime.now() - start))
        else:
            start = datetime.now()
            self.gensim_word2vec = gensim.models.Word2Vec(
                sentences=self.sentences, size=300, window=5,
                min_count=0, workers=4, sg=0)
            self.gensim_word2vec.save(DEFAULT_LOCATION)
            logger.info('Not found pretrained model - Created newly Word2Vector at {} - training time {}'.
                        format(DEFAULT_LOCATION, datetime.now() - start))

    def filter_overlapped_sentences(self):
        start = datetime.now()
        vocabulary = np.array(self.gensim_word2vec.wv.index2word)
        ohv_sentence = np.array([np.isin(vocabulary, sentence).astype(np.int32) for sentence in self.sentences])
        mask_ones = np.ones(ohv_sentence.shape[1])
        non_overlapped_indices = ohv_sentence @ mask_ones.T == 0
        logger.info('Filtering Overlapped sentences in pretrained Word2Vector model {}'.format(datetime.now() - start))
        return np.array(self.sentences)[non_overlapped_indices].tolist()

    def get_model(self):
        return self.gensim_word2vec


class TopicModelling:
    def __init__(self):
        pass

    @staticmethod
    def apply_lda(sentences):
        def format_topics_sentences(ldamodel, local_corpus, texts):
            # Init output
            sent_topics_df = pd.DataFrame()

            # Get main topic in each document
            for _i, row_list in enumerate(ldamodel[local_corpus]):
                row = row_list[0] if ldamodel.per_word_topics else row_list
                row = sorted(row, key=lambda x: (x[1]), reverse=True)
                # Get the Dominant topic, Perc Contribution and Keywords for each document
                for _j, (topic_num, prop_topic) in enumerate(row):
                    if j == 0:  # => dominant topic
                        wp = ldamodel.show_topic(topic_num)
                        topic_keywords = ", ".join([_word for _word, prop in wp])
                        sent_topics_df = sent_topics_df.append(
                            pd.Series([int(topic_num), round(prop_topic, 4), topic_keywords]), ignore_index=True)
                    else:
                        break
            sent_topics_df.columns = ['Dominant_Topic', 'Perc_Contribution', 'Topic_Keywords']

            # Add original text to the end of the output
            contents = pd.Series(texts)
            sent_topics_df = pd.concat([sent_topics_df, contents], axis=1)
            return sent_topics_df

        id2word = gensim.corpora.Dictionary(sentences)
        corpus = [id2word.doc2bow(text) for text in sentences]
        lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                                    id2word=id2word,
                                                    num_topics=4,
                                                    update_every=1,
                                                    chunksize=10,
                                                    passes=10,
                                                    alpha='symmetric',
                                                    per_word_topics=True)
        topics = lda_model.print_topics()
        for topic in topics:
            logger.info(topic)

        df_topic_sents_keywords = format_topics_sentences(ldamodel=lda_model, local_corpus=corpus, texts=sentences)
        df_dominant_topic = df_topic_sents_keywords.reset_index()
        df_dominant_topic.columns = ['Document_No', 'Dominant_Topic', 'Topic_Perc_Contrib', 'Keywords', 'Text']

        sent_topics_sorteddf_mallet = pd.DataFrame()
        sent_topics_outdf_grpd = df_topic_sents_keywords.groupby('Dominant_Topic')
        for i, grp in sent_topics_outdf_grpd:
            sent_topics_sorteddf_mallet = pd.concat([sent_topics_sorteddf_mallet,
                                                     grp.sort_values(['Perc_Contribution'], ascending=False).head(1)],
                                                    axis=0)
        sent_topics_sorteddf_mallet.reset_index(drop=True, inplace=True)
        sent_topics_sorteddf_mallet.columns = ['Topic_Num', "Topic_Perc_Contrib", "Keywords", "Representative Text"]

        doc_lens = [len(d) for d in df_dominant_topic.Text]
        # Plot
        fig1 = plt.figure(figsize=(16, 7), dpi=100)
        plt.hist(doc_lens, bins=1000, color='navy')
        plt.text(750, 100, "Mean   : " + str(np.round(np.mean(doc_lens))))
        plt.text(750, 90, "Median : " + str(np.round(np.median(doc_lens))))
        plt.text(750, 80, "Stdev   : " + str(np.round(np.std(doc_lens))))
        plt.text(750, 70, "1%ile    : " + str(np.round(np.quantile(doc_lens, q=0.01))))
        plt.text(750, 60, "99%ile  : " + str(np.round(np.quantile(doc_lens, q=0.99))))

        plt.gca().set(xlim=(0, 1000), ylabel='Number of Documents', xlabel='Document Word Count')
        plt.tick_params(size=16)
        plt.xticks(np.linspace(0, 1000, 9))
        plt.title('Distribution of Document Word Counts', fontdict=dict(size=22))

        cols = [color for name, color in mcolors.TABLEAU_COLORS.items()]  # more colors: 'mcolors.XKCD_COLORS'
        fig2, axes = plt.subplots(2, 2, figsize=(16, 14), dpi=100, sharex=True, sharey=True)

        for i, ax in enumerate(axes.flatten()):
            df_dominant_topic_sub = df_dominant_topic.loc[df_dominant_topic.Dominant_Topic == i, :]
            doc_lens = [len(d) for d in df_dominant_topic_sub.Text]
            ax.hist(doc_lens, bins=1000, color=cols[i])
            ax.tick_params(axis='y', labelcolor=cols[i], color=cols[i])
            sns.kdeplot(doc_lens, color="black", shade=False, ax=ax.twinx())
            ax.set(xlim=(0, 1000), xlabel='Document Word Count')
            ax.set_ylabel('Number of Documents', color=cols[i])
            ax.set_title('Topic: ' + str(i), fontdict=dict(size=16, color=cols[i]))

        fig2.tight_layout()
        fig2.subplots_adjust(top=0.90)
        plt.xticks(np.linspace(0, 1000, 9))
        fig2.suptitle('Distribution of Document Word Counts by Dominant Topic', fontsize=22)

        cols = [color for name, color in mcolors.TABLEAU_COLORS.items()]  # more colors: 'mcolors.XKCD_COLORS'
        cloud = WordCloud(background_color='white',
                          width=2500,
                          height=1800,
                          max_words=10,
                          colormap='tab10',
                          color_func=lambda *args, **kwargs: cols[i],
                          prefer_horizontal=1.0)

        topics = lda_model.show_topics(formatted=False)

        fig3, axes = plt.subplots(2, 2, figsize=(10, 10), sharex=True, sharey=True)

        for i, ax in enumerate(axes.flatten()):
            fig3.add_subplot(ax)
            topic_words = dict(topics[i][1])
            cloud.generate_from_frequencies(topic_words, max_font_size=300)
            plt.gca().imshow(cloud)
            plt.gca().set_title('Topic ' + str(i), fontdict=dict(size=16))
            plt.gca().axis('off')

        plt.subplots_adjust(wspace=0, hspace=0)
        plt.axis('off')
        plt.margins(x=0, y=0)
        plt.tight_layout()

        topics = lda_model.show_topics(formatted=False)
        data_flat = [w for w_list in sentences for w in w_list]
        counter = Counter(data_flat)
        out = []
        for i, topic in topics:
            for word, weight in topic:
                out.append([word, i, weight, counter[word]])

        df = pd.DataFrame(out, columns=['word', 'topic_id', 'importance', 'word_count'])

        # Plot Word Count and Weights of Topic Keywords
        fig4, axes = plt.subplots(2, 2, figsize=(16, 10), sharey=True, dpi=100)
        cols = [color for name, color in mcolors.TABLEAU_COLORS.items()]
        for i, ax in enumerate(axes.flatten()):
            ax.bar(x='word', height="word_count", data=df.loc[df.topic_id == i, :], color=cols[i], width=0.5, alpha=0.3,
                   label='Word Count')
            ax_twin = ax.twinx()
            ax_twin.bar(x='word', height="importance", data=df.loc[df.topic_id == i, :], color=cols[i], width=0.2,
                        label='Weights')
            ax.set_ylabel('Word Count', color=cols[i])
            ax_twin.set_ylim(0, 0.030)
            ax.set_ylim(0, 3500)
            ax.set_title('Topic: ' + str(i), color=cols[i], fontsize=16)
            ax.tick_params(axis='y', left=False)
            ax.set_xticklabels(df.loc[df.topic_id == i, 'word'], rotation=30, horizontalalignment='right')
            ax.legend(loc='upper left')
            ax_twin.legend(loc='upper right')

        fig4.tight_layout(w_pad=2)
        fig4.suptitle('Word Count and Importance of Topic Keywords', fontsize=22, y=1.05)

        start = 0
        end = 13
        corp = corpus[start:end]
        mycolors = [color for name, color in mcolors.TABLEAU_COLORS.items()]

        fig5, axes = plt.subplots(end - start, 1, figsize=(20, (end - start) * 0.95), dpi=100)
        axes[0].axis('off')
        for i, ax in enumerate(axes):
            if i > 0:
                corp_cur = corp[i - 1]
                topic_percs, wordid_topics, wordid_phivalues = lda_model[corp_cur]
                word_dominanttopic = [(lda_model.id2word[wd], topic[0]) for wd, topic in wordid_topics]
                ax.text(0.01, 0.5, "Doc " + str(i - 1) + ": ", verticalalignment='center',
                        fontsize=16, color='black', transform=ax.transAxes, fontweight=700)

                # Draw Rectange
                topic_percs_sorted = sorted(topic_percs, key=lambda x: (x[1]), reverse=True)
                ax.add_patch(Rectangle((0.0, 0.05), 0.99, 0.90, fill=None, alpha=1,
                                       color=mycolors[topic_percs_sorted[0][0]], linewidth=2))

                word_pos = 0.06
                for j, (word, topics) in enumerate(word_dominanttopic):
                    if j < 14:
                        ax.text(word_pos, 0.5, word,
                                horizontalalignment='left',
                                verticalalignment='center',
                                fontsize=16, color=mycolors[topics],
                                transform=ax.transAxes, fontweight=700)
                        word_pos += .009 * len(word)  # to move the word for the next iter
                        ax.axis('off')
                ax.text(word_pos, 0.5, '. . .',
                        horizontalalignment='left',
                        verticalalignment='center',
                        fontsize=16, color='black',
                        transform=ax.transAxes)

        plt.subplots_adjust(wspace=0, hspace=0)
        plt.suptitle('Sentence Topic Coloring for Documents: ' + str(start) + ' to ' + str(end - 2), fontsize=22,
                     y=0.95, fontweight=700)
        plt.tight_layout()

        html1 = mpld3.fig_to_html(fig1)
        html2 = mpld3.fig_to_html(fig2)
        html3 = mpld3.fig_to_html(fig3)
        html4 = mpld3.fig_to_html(fig4)
        html5 = mpld3.fig_to_html(fig5)

        serve(html1 + html2 + html3 + html4 + html5)
