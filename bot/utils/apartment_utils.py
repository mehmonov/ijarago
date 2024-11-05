async def select_best_apartment(apartments: list) -> dict:
    if not apartments:
        return None
    
    # Har bir kvartira uchun ball hisoblash
    scored_apartments = []
    for apt in apartments:
        score = 0
        
        # Mebellar uchun +2 ball
        if apt['has_furniture']:
            score += 2
        
        # Qavatlar soni uchun ball (ko'proq = yaxshiroq)
        score += float(apt['total_floors']) * 0.1
        
        # Maydon uchun ball (kattaroq = yaxshiroq)
        score += float(apt['area']) * 0.05
        
        # Narx uchun ball (arzonroq = yaxshiroq)
        price_score = 5 - (float(apt['price']) / 100000)  # har 100k uchun -1 ball
        score += max(0, price_score)
        
        scored_apartments.append((score, apt))
    
    # Eng ko'p ball to'plagan kvartira
    return max(scored_apartments, key=lambda x: x[0])[1]
