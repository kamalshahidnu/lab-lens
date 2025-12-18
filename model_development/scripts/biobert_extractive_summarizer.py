# model-development/scripts/biobert_extractive_summarizer.py

import numpy as np
from transformers import AutoModel, AutoTokenizer


class MedicalReportSummarizer:
    def __init__(self):
        # Load BioBERT
        self.tokenizer = AutoTokenizer.from_pretrained("dmis-lab/biobert-base-cased-v1.2")
        self.model = AutoModel.from_pretrained("dmis-lab/biobert-base-cased-v1.2")

    def summarize(self, row):
        """
        Uses your features + BioBERT to create summary
        """
        text = row["cleaned_text_final"]
        sentences = text.split(". ")

        # Score sentences using your features
        sentence_scores = []
        for sent in sentences:
            score = self._calculate_importance(sent, row)
            sentence_scores.append(score)

        # Get BioBERT embeddings for semantic importance
        biobert_scores = self._get_biobert_scores(sentences)

        # Combine scores (your features + BioBERT)
        final_scores = [
            0.6 * feat_score + 0.4 * bert_score
            for feat_score, bert_score in zip(sentence_scores, biobert_scores)
        ]

        # Select top sentences
        top_indices = np.argsort(final_scores)[-5:]  # Top 5 sentences
        summary = ". ".join([sentences[i] for i in sorted(top_indices)])

        return summary

    def _calculate_importance(self, sentence, features):
        """Use your 47 features to score sentence importance"""
        score = 0

        # Urgent cases - prioritize severity indicators
        if features["urgency_indicator"] == 1:
            if any(
                word in sentence.lower()
                for word in ["critical", "urgent", "severe", "immediate"]
            ):
                score += 2.0

        # Abnormal lab values - include specific findings
        if features["abnormal_lab_count"] > 0:
            if any(
                word in sentence.lower() for word in ["abnormal", "elevated", "low"]
            ):
                score += 1.5

        return score

    def _get_biobert_scores(self, sentences):
        """Get BioBERT semantic scores for sentences"""
        scores = []
        for sent in sentences:
            inputs = self.tokenizer(
                sent, return_tensors="pt", truncation=True, max_length=512
            )
            outputs = self.model(**inputs)
            # Use CLS token embedding magnitude as importance
            score = outputs.last_hidden_state[:, 0, :].mean().item()
            scores.append(score)
        return scores
