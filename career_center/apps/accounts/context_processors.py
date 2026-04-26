def ui_labels(_request):
    return {
        'STATUS_LABELS': {
            'active': 'Активно',
            'hidden': 'Скрыто',
            'archive': 'Архив',
            'pending': 'Ожидает проверки',
            'approved': 'Подтверждено',
            'rejected': 'Отклонено',
        },
        'FORMAT_LABELS': {
            'online': 'Онлайн',
            'offline': 'Очно',
        },
        'KIND_LABELS': {
            'course': 'Курс',
            'seminar': 'Семинар',
            'practice': 'Практика',
        },
    }
