from user.models import Progress
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

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

def fetch_progress_data():
    progress_entries = Progress.objects.all().values('user__username', 'exercise__title', 'status', 'score', 'time_spent')

    df = pd.DataFrame(progress_entries)

    df['time_spent_seconds'] = df['time_spent'].apply(lambda x: x.total_seconds() if x is not None else 0)

    label_encoder = LabelEncoder()
    df['status_encoded'] = label_encoder.fit_transform(df['status'])

    user_avg_score = df.groupby('user__username')['score'].mean().reset_index()
    user_avg_time_spent = df.groupby('user__username')['time_spent_seconds'].mean().reset_index()

    df = pd.merge(df, user_avg_score, on='user__username', suffixes=('', '_avg'))
    df = pd.merge(df, user_avg_time_spent, on='user__username', suffixes=('', '_avg'))

    scaler = MinMaxScaler()
    df[['score', 'time_spent_seconds']] = scaler.fit_transform(df[['score', 'time_spent_seconds']])

    return df

def train_model(df):
    # Features: User's average score, average time spent, exercise status encoding
    features = ['score_avg', 'time_spent_seconds_avg', 'status_encoded']
    X = df[features]

    y = df['status'].apply(lambda x: 1 if x == 'completed' else 0)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print(f"Accuracy: {accuracy_score(y_test, y_pred)}")
    print(classification_report(y_test, y_pred))

    return model

data = fetch_progress_data()

model = train_model(data)

def suggest_exercises(user_id):
    user_data = data[data['user__username'] == user_id]

    print("hi", user_data)
    suggestions = []
    for _, row in user_data.iterrows():
        features = [row['score_avg'], row['time_spent_seconds_avg'], row['status_encoded']]
        prediction = model.predict([features])[0]
        if prediction == 1:
            suggestions.append(row['exercise__title'])

    print(suggestions)
    return suggestions