from weasyprint import HTML, CSS
from datetime import datetime
import os


def generate_grant_pdf(filepath, user, gpa):
    """
    Generate grant request PDF using WeasyPrint
    """
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Times New Roman', serif;
                margin: 50px;
                font-size: 14pt;
            }}
            .header {{
                text-align: right;
                line-height: 1.5;
                margin-bottom: 30px;
                font-weight: bold; 
            }}
            .title {{
                text-align: center;
                font-weight: bold;
                font-size: 16pt;
                margin-bottom: 20px;
            }}
            .content {{
                text-align: justify;
                line-height: 1.6;
            }}
            .footer {{
                margin-top: 60px;
                text-align: left;
                font-size: 12pt;
                display: flex;
                flex-direction: row;
                gap: 40px; 
                font-weight: bold; 
            }}
        </style>
    </head>
    <body>
        <div class="header">
            Navoiy davlat konchilik va texnologiyalar universiteti<br/>
            rektori B.T. Mardonovga<br/>
        </div>

        <div class="title">Ariza</div>

        <div class="content">
        Men {user.full_name} {user.faculty} fakultetining {user.level} {user.educationType} {user.group} guruhida tahsil olaman. 2024-2025 o‘quv yili uchun GPA ko‘rsatkichim {gpa}.
            
            Menga 2025-2026 o‘quv yili uchun Oʻzbekiston Respublikasi Vazirlar Mahkamasining “Oliy taʼlim tashkilotlarida talabalarga grantlarni taqdim etish va qayta taqsimlash tartibi toʻgʻrisidagi nizomni tasdiqlash haqida” 2025-yil 10-martdagi 149-sonli qarori bilan tasdiqlangan Nizomga muvofiq ta’lim grantiga talabgor sifatida ishtirok etishga ruxsat berishingizni so‘rayman.
        </div>

        <div class=educationType"footer">
          <div> {user.full_name}</div>   
          <div> {user.student_id_number}</div>  
          <div> {datetime.now().strftime('%Y-%m-%d')}</div>  
        </div>
    </body>
    </html>
    """

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    HTML(string=html).write_pdf(filepath)


def generate_rejection_pdf(filepath, user, gpa):
    """
    Generate rejection PDF for GPA < 3.5 using WeasyPrint
    """
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Times New Roman', serif;
                margin: 50px;
                font-size: 14pt;
            }}
            .greeting {{
                margin-bottom: 30px;
            }}
            .content {{
                text-align: justify;
                line-height: 1.6;
            }}
            .footer {{
                margin-top: 60px;
                text-align: left;
                font-size: 12pt;
            }}
        </style>
    </head>
    <body>
        <div class="greeting">
            Hurmatli {user.full_name}!
        </div>

        <div class="content">
            Sizning GPA balingiz {gpa}, ya’ni Vazirlar Mahkamasining 149-sonli qarori bilan
            tasdiqlangan Nizomning 2-bobi, 13-xat boshida keltirilgan "Ta’lim grantiga
            talabgorlardan joriy o‘quv yilida o‘zlashtirish ko‘rsatkichi bo‘yicha GPA
            ko‘rsatkichi 3.5 va undan yuqori bo‘lishi talab etiladi" degan talablarga ko‘ra,
            GPA ko‘rsatkichi 3.5 dan kam bo‘lganligi sababli, Oliy ta’lim tashkilotlarida
            talabalarga grantlarni taqdim etish va qayta taqsimlash bo‘yicha tanlovda ishtirok eta olmaysiz.
        </div>

        <div class="footer">
            Sana: {datetime.now().strftime('%Y-%m-%d')}
        </div>
    </body>
    </html>
    """

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    HTML(string=html).write_pdf(filepath)


