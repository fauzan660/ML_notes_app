

# model = SentenceTransformer("sentence-transformers/msmarco-MiniLM-L6-cos-v5")

def transformer_similarity(text1, text2):
    from sentence_transformers import SentenceTransformer, util
    return 1
    # emb1 = model.encode(text1, convert_to_tensor=True, normalize_embeddings=True)
    # emb2 = model.encode(text2, convert_to_tensor=True, normalize_embeddings=True)

    # score = util.cos_sim(emb1, emb2).item()  # scalar value between -1 and 1

    # # Map to 0–5 scale for UI purposes
    # score_scaled = 5 * (score + 1) / 2
    # return round(score_scaled, 3)
