import os, re
class Preprocessor():
    def __init__(self, path_to_corpus = "data/OpenEDGeS/", path_to_processed_data = "data/processed/"):
        self.path_to_corpus = path_to_corpus
        self.path_to_processed_data = path_to_processed_data
        print("Initializing preprocessor...\nCorpus directory:", self.path_to_corpus)
        print("Output directory:", self.path_to_processed_data)
    
    def set_alignment_info(self, s_alignment_file, verbose = False):
        # GET PATH TO F/E TEXTS
        self.s_alignment_file = s_alignment_file
        tsv_name = os.path.basename(self.s_alignment_file)
        # get names of the f/e texts from the tsv, e.g. 'en_1833_Webster'
        f_and_e, _ = tsv_name.split(sep='.')
        f_text, e_text = f_and_e.split(sep='-')
        # language, year and edition e.g. 'en', '1833', 'Webster'
        f_lang, f_yr, f_ed = f_text.split(sep='_')
        e_lang, e_yr, e_ed = e_text.split(sep='_')
        # path to the folder containing f/e texts
        # e.g. 'data/OpenEDGeS/Texts/en/en_1833_Webster'
        self.path_to_f = self.path_to_corpus + "Texts/" + f_lang + "/" + f_text
        self.path_to_e = self.path_to_corpus + "Texts/" + e_lang + "/" + e_text
        if os.path.exists(self.path_to_f) and os.path.exists(self.path_to_e):
            # path to output of processing
            output_path = self.path_to_processed_data + f_lang + "-" + e_lang + "/" + f_and_e + "/"
            os.makedirs(output_path, exist_ok = True)
            self.output_f = output_path + "text.f"
            self.output_e = output_path + "text.e"
            if verbose:
                print("Processing alignment file:", self.s_alignment_file)
                print("Directory to f text:", self.path_to_f)
                print("Directory to e text:", self.path_to_e)
                print("Outputing .f file:", self.output_f)
                print("Outputing .e file:", self.output_e)
            return True
        else:
            print("Processing alignment file:", self.s_alignment_file)
            print("Coressponding texts missing, skipping...")
            return False
        

    # clean up sentence and tokenization
    def clean_sentence(self, sent):
        sent = re.sub('{|}|\[|\]', '', sent)
        sent_tokenized = re.findall(r"\w+|[^\w\s]", sent)
        sent = " ".join(sent_tokenized)
        return sent

    # utility function
    def read_book(self, book_path):
        book = ['<START>']
        with open(book_path, 'r') as reader:
            for line in reader.readlines():
                verse_num, sent = line.strip().split(sep='\t') # get the verse&sentence
                sent = self.clean_sentence(sent) # tokenization
                if verse_num.endswith('.0'):
                    book.append('<NON-VERSE>') # handle non-verse lines
                else:
                    book.append(sent)
        return book

    # function to read alignment file
    def get_alignments(self, a_file):
        f_alignments = []
        e_alignments = []
        with open(a_file, mode='r') as f:
            for sent in f.readlines():
                f_line_refs, e_line_refs = sent.strip().split(sep='\t')
                f_line_refs = f_line_refs.strip().split(sep=',')
                e_line_refs = e_line_refs.strip().split(sep=',')
                f_alignments.append(f_line_refs)
                e_alignments.append(e_line_refs)
        return f_alignments, e_alignments

    # function to retrieve sentences
    def retrieve_sents(self, alignments, path_to_x):
        output_sents = []
        current_bk_path = ''
        current_bk = [] # current book in memory
        for line_refs in alignments:
            lines = []
            for line_ref in line_refs:
                # for each of the line reference
                # determine the corresponding book file
                bk_name, line_num = line_ref.split(sep='.')
                bk_path = path_to_x + '/' + bk_name + '.tsv'
                # update book in memory if needed
                if bk_path != current_bk_path:
                    current_bk_path = bk_path
                    current_book = self.read_book(current_bk_path)
                # retrieve line from book
                line = current_book[int(line_num)]
                lines.append(line)
            # combine lines
            output_sent = ' '.join(lines)
            output_sents.append(output_sent)
        return output_sents
    
    # writer
    def write_to_output(self, sents, output_file):
        with open(output_file, mode='w') as writer:
            for sent in sents:
                writer.write(sent + '\n')
        return None

    # main function for prcessing
    def process(self, input_file, verbose = True):
        exists = self.set_alignment_info(input_file, verbose)
        if exists:
            f_alignments, e_alignments = self.get_alignments(self.s_alignment_file)
            f_sents = self.retrieve_sents(f_alignments, self.path_to_f)
            self.write_to_output(f_sents, self.output_f)
            e_sents = self.retrieve_sents(e_alignments, self.path_to_e)
            self.write_to_output(e_sents, self.output_e)