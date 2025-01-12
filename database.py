import asyncpg
from datetime import datetime, timedelta
from config import DATABASE

async def get_daily_statistics():
    """
    Получает статистику эмоций за последние 24 часа по всем учреждениям
    """
    try:
        conn = await asyncpg.connect(**DATABASE)
        
        query = """
            SELECT 
                institutions.name,
                COUNT(events.event_id) as total_emotions,
                COUNT(CASE WHEN events.user_id IS NOT NULL THEN 1 END) as registered_emotions,
                events.emotion,
                COUNT(events.emotion) as emotion_count
            FROM events
            JOIN institutions ON events.institution_id = institutions.id
            WHERE events.time >= $1
            GROUP BY institutions.name, events.emotion
            ORDER BY institutions.name, events.emotion
        """
        
        yesterday = datetime.now() - timedelta(days=1)
        rows = await conn.fetch(query, yesterday)
        
        statistics = []
        current_institution = None
        institution_data = None
        
        for row in rows:
            if current_institution != row['name']:
                if institution_data:
                    statistics.append(institution_data)
                current_institution = row['name']
                institution_data = {
                    'name': row['name'],
                    'date': yesterday.strftime('%d.%m.%Y'),
                    'total_emotions': row['total_emotions'],
                    'registered_emotions': row['registered_emotions'],
                    'emotions_breakdown': {}
                }
            
            institution_data['emotions_breakdown'][row['emotion']] = row['emotion_count']
        
        if institution_data:
            statistics.append(institution_data)
        
        await conn.close()
        return statistics
        
    except Exception as e:
        print(f"Ошибка при получении статистики: {e}")
        return [] 