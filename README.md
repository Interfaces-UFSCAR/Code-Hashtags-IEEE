# Code-Hashtags-IEEE
Repository with the code related to the article publication, regarding the construction and labeling of the ITED-Br hashtags Graph (runoffs); and the following user ideology score calculation based on the labeled graph.

The study ran this code togethr with a local copy of the hydrated ITED-Br dataset. More specifically, it targeted a political context which is cointained by thataset, the 2022 Brasilian presidential elections runoffs.
For that purpose, it collected a subset of data pertaining to october of that year, from the 3rd to the 31st. Since the runnoffs were between candidates Lula and Bolsonaro, the study targeted the subqueries retweets_query_lula, query_lula, retweets_query_bolsonaro and query_bolsonaro, whose descriptions can be found in the study attached to the repository of the ITED-Br dataset (https://github.com/Interfaces-UFSCAR/ITED-Br).

The local copy must be structured in the same manner that can be encountered in the ITED-Br dataset repositery, with the exception that it must also contain the hydrated tweet and user files, for these scripts to work, unless modifications are made.

# Pipeline

## collect_hashtags.py

The hashtags are collected from the subset with use of **collect_hashtags.py**. The same script also creates the sparse coocurrence matrices using the collected hashtags.

input args: **corpus_path**; **lula_prelabeled**; **bolsonaro_prelabeled**

output args: **lula_hashtags_output**; **bolsonaro_hashtags_output**; **lula_matrix_output**; **bolsonaro_matrix_output**

**Expected and resulting file types:**

lula_prelabeled (**xlsx**); bolsonaro_prelabeled (**xlsx**); lula_hashtags_output (**csv**); bolsonaro_hashtags_output (**csv**); lula_matrix_output (**npz**); bolsonaro_matrix_output (**npz**)

**OBS:** The npz generated npz files do not strictly follow the regular npz format specifications - the index (hashtag names) is also added at the beginning of the file. This is also true and expected for the rest of this pipeline.

---

## hashtags_label_spreading.py

**hashtags_label_spreading.py** uses the generated matrices, together with pre-labeled data (subset of the collected hashtags) to finish labeling the given matrices, as possible, according to a label spreading algorithm.

input and output args: **--candidate** (quadruple: matrix file, prelabeled hashtags file, csv output and json output, separated by space. Can be used multiple times to process data regarding multiple candidates)

**Expected and resulting file types:**

candidate[0] (**npz**); candidate[1] (**xlsx**); candidate[2] (**csv**); candidate[3] (**json**)

---

## serialize_coocc_graphs.py

**serialize_coocc_graphs.py** is used to create a json representation of the graphs represented by the matrices which can then be displayed in most graph rendering software, including the one used by the researchers in this study (developed internally), which used the sigma.js framework - [sigmajs.org/](https://www.sigmajs.org/).

input and output args: **--candidate** (pair: matrix file, and output file, separated by space. Can be used multiple times to process data regarding multiple candidates)

**Expected and resulting file types:**

candidate[0] (npz); candidate[1] (**json**)

---

## g_apply_class_as_colors.py

**g_apply_class_as_colors.py** is used to modify the serialized graphs, applying the classes predicted with serialize_coocc_graphs.py as colors to the nodes representing each hashtag in the graphs.

input and output args: **--candidate** (triple: input graph file, labeled hashtags file and output graph file, separated by space. Can be used multiple times to process data regarding multiple candidates)

**Expected and resulting file types:**

candidate[0] (**json**); candidate[1] (**json**); candidate[2] (**json**)

---

## colored_g_apply_frequency_as_size.py

**colored_g_apply_frequency_as_size.py** was used to scale node sizes and edge visibility based on hashtag frequency (as encountered in the studied corpus subset) to improve visualization clarity and quality.

input and output args: **--candidate** (triple: input graph file, hashtag frequency file, and output graph file separated by space. Can be used multiple times to process data regarding multiple candidates)

**Expected and resulting file types:**

candidate[0] (**json**); candidate[1] (**csv**); candidate[2] (**json**)

---

## classify_users.py

**classify_users.py** is used to, given the resulting classifications regarding the hashtags extracted from the corpus substet, classify users which used those hashtags in their tweets, according to the usage of each class of hashtag by each user.

input args: **corpus_path**; **lula_labeled_hashtags**; **bolsonaro_labeled_hashtags**

output args: **lula_classification_output**; **bolsonaro_classification_output**

**Expected and resulting file types:**

lula_labeled_hashtags (**csv**); bolsonaro_labeled_hashtags (**csv**); lula_classification_output (**csv**); bolsonaro_classification_output (**csv**)

---

## plots.py

**plots.py** is used to generate the plots showing the distribultions resultant of the user classification process.

input args: **classified_users_lula**, **classified_users_bolsonaro**;

output args: **output_file_path_lula**, **output_file_path_bolsonaro**;

**Expected and resulting file types:**

classified_users_lula (**csv**); classified_users_bolsonaro (**csv**); output_file_path_lula (**png**); output_file_path_bolsonaro (**png**)

---

## user_ideology_wordclouds.py

**user_ideology_wordclouds.py** is used to generate the wordclours representing the presence of the hashtags found in the subset.

input args: **lula_labels**; **bolsonaro_labels**; **lula_frequency**; **bolsonaro_frequency**; --remove_prelabeled (optional, pair: lula prelabeled hashtags file and bolsonaro prelabeled hashtags file)

output args: **lula_outputs** (triple: pro category output file, anti category output file and indef category output file); **bolsonaro_outputs** (triple: pro category output file, anti category output file and indef category output file)

**Expected and resulting file types:**

lula_labels (**csv**); bolsonaro_labels (**csv**); lula_frequency (**csv**); bolsonaro_frequency (**csv**); lula_outputs[0] (**png**); lula_outputs[1] (**png**); lula_outputs[2] (**png**); bolsonaro_outputs[0] (**png**); bolsonaro_outputs[1] (**png**); bolsonaro_outputs[2] (**png**); remove_prelabeled[0] (**xlsx**); remove_prelabeled[1] (**xlsx**)

---

## corpus.py and serialization.py

**corpus.py** and **serialization.py** are imported by the previoulsy mentioned scripts, providing support functions regarding the access and collection of data from corpus subsets, and serialization and loading of matrix and graph data, respectively.

# Data Usage Agreement
This software and its source code are licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International Public License (CC BY-NC-SA 4.0). By using either, you agree to abide by the stipulations in the license and cite the following manuscript:
Iasulaitis, S.; Valejo, A.D.; Greco, B.C.; Ruiz, I.V.R; Perillo, V.G.; Messias, G.H.; Vicari, I. Political Hashtag Networks and Polarization in Brazil:
A Machine Learning Analysis on Social Networks. Journal of Computational Social Science (2025). (PUBLICATION DOI PLACEHOLDER).
