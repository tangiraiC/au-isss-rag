import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import glob

class Retriever:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.df = self._load_data()
        self.vectorizer = None
        self.tfidf_matrix = None
        self._build_index()

    def _load_data(self):
        all_dfs = []
        
        # Load processed_data/isss_data.csv (Scraped web data)
        isss_path = os.path.join(self.data_dir, 'isss_data.csv')
        if os.path.exists(isss_path):
            df_isss = pd.read_csv(isss_path)
            # Standardize columns
            # Web CSV: Source URL, Section, Text, Link Text, URL
            # We want: content, source, metadata
            df_isss['content'] = df_isss['Section'] + ": " + df_isss['Text']
            df_isss['source'] = df_isss['Source URL']
            df_isss['type'] = 'web'
            all_dfs.append(df_isss[['content', 'source', 'type']])

        # Load processed_data/rag_data.csv (Converted documents)
        rag_path = os.path.join(self.data_dir, 'rag_data.csv')
        if os.path.exists(rag_path):
            df_rag = pd.read_csv(rag_path)
            # Doc CSV: id, source, context, text
            df_rag['content'] = df_rag['context'].fillna('') + "\n" + df_rag['text']
            df_rag['type'] = 'document'
            all_dfs.append(df_rag[['content', 'source', 'type']])

        if not all_dfs:
            return pd.DataFrame(columns=['content', 'source', 'type'])

        return pd.concat(all_dfs, ignore_index=True)

    def _build_index(self):
        if self.df.empty:
            print("Warning: No data loaded for retrieval.")
            return

        # Simple TF-IDF
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df['content'].fillna(''))
        print(f"Index built with {len(self.df)} documents.")

    def search(self, query, top_k=5):
        if self.vectorizer is None or self.tfidf_matrix is None:
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get top k indices
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0: # Only return relevant results
                results.append({
                    'content': self.df.iloc[idx]['content'],
                    'source': self.df.iloc[idx]['source'],
                    'score': float(similarities[idx]),
                    'type': self.df.iloc[idx]['type']
                })
        
        return results

if __name__ == "__main__":
    # Test
    retriever = Retriever("../../processed_data")
    results = retriever.search("Optional Practical Training")
    for r in results:
        print(f"[{r['score']:.2f}] {r['source']}: {r['content'][:100]}...")
