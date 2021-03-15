# Extending IBM Word Alignment Model 1 with Edit Distance
## Results on a Diachronic Parallel Corpus (CL Final Project, Winter 20/21)
## Siyu Tao

To recreate the experiment results, use code in the Jupyter Notebook `notebook.ipynb`. Preprocessed data needed is already included in this repo/submission, so the preprocessing steps can be skipped if so desired.

All .py code are my own, `score-alingment` script is from [jhu-mt-hw](https://github.com/xutaima/jhu-mt-hw/blob/master/hw2/score-alignments).

File Structure

Notebook:
```
└── notebook.ipynb
notebook.ipynb
```

Python scripts:
```
./bin/
├── ed_model.py
├── model1.py
├── preprocessing.py
└── score-alignments
```

Data for evaluation incl. gold sets:
```
./data/eval
├── de-de
│   └── de_1781_Rosalino-de_1871_Elberfelder
│       ├── text.a
│       ├── text.e
│       └── text.f
├── de-en
│   └── de_1871_Elberfelder-en_1890_Darby
│       ├── text.a
│       ├── text.e
│       └── text.f
└── en-en
    └── en_1611_KJV-en_1890_Darby
        ├── text.a
        ├── text.e
        └── text.f
```

Experiment output incl. summary:
```
./output
├── de-de_ed1.a
├── de-de_ed1.log
├── de-de_ed2.a
├── de-de_ed2.log
├── de-de_ibm1.a
├── de-de_ibm1.log
├── de-en_ed1.a
├── de-en_ed1.log
├── de-en_ed2.a
├── de-en_ed2.log
├── de-en_ibm1.a
├── de-en_ibm1.log
├── en-en_ed1.a
├── en-en_ed1.log
├── en-en_ed2.a
├── en-en_ed2.log
├── en-en_ibm1.a
├── en-en_ibm1.log
└── summary.info
```