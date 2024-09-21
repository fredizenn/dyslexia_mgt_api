from user.models import Progress


def get_next_difficulty(user):
    progress = Progress.objects.filter(user=user).order_by('-last_updated')[:5]  # Last 5 exercises
    
    if not progress:
        return 1  # Start with easy (difficulty level 1)

    avg_score = sum([p.score for p in progress]) / len(progress)
    
    if avg_score > 85:
        return 3  # hard
    elif avg_score > 70:
        return 2  # medium
    else:
        return 1  # easy
