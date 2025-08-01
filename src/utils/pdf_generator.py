from weasyprint import HTML
from datetime import datetime
import os
import uuid


def generate_application_pdf(filepath, user, gpa):
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
                
                font-size: 14pt;
            }}
            .header {{
                text-align: right;
                line-height: 1.5;
                margin-bottom: 15px;
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
                flex-direction: column;
                gap: 20px; 
                font-weight: bold; 
            }}
        </style>
    </head>
    <body>
        <div class="header">
            Navoiy davlat konchilik va<br/> texnologiyalar universiteti<br/>
            rektori B.T. Mardonovga<br/>
        </div>

        <div class="title">Ariza</div>

        <div class="content" style="text-indent: 40px">
        Men {user.full_name} {user.faculty} fakultetining {user.level} {user.education_type} {user.group} guruhida tahsil olaman. 2024-2025 o‘quv yili uchun GPA ko‘rsatkichim {gpa}.
            
            Menga 2025-2026 o‘quv yili uchun Oʻzbekiston Respublikasi Vazirlar Mahkamasining “Oliy taʼlim tashkilotlarida talabalarga grantlarni taqdim etish va qayta taqsimlash tartibi toʻgʻrisidagi nizomni tasdiqlash haqida” 2025-yil 10-martdagi 149-sonli qarori bilan tasdiqlangan Nizomga muvofiq ta’lim grantiga talabgor sifatida ishtirok etishga ruxsat berishingizni so‘rayman.
        </div>

        <div class="footer">
          <div>F.I.O:  {user.full_name}</div>   
          <div  >Talaba ID raqami:  {user.student_id_number}</div>  
          <div> Ariza berilgan sana:  {datetime.now().strftime('%Y-%m-%d')}</div>  
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
        <div class="greeting" >
           <b> Hurmatli {user.full_name}! </b>
        </div>

        <div class="content" style="text-indent: 40px">
            Sizning GPA balingiz {gpa}, ya’ni Vazirlar Mahkamasining 149-sonli qarori bilan
            tasdiqlangan Nizomning 2-bobi, 13-xat boshida keltirilgan "Ta’lim grantiga
            talabgorlardan joriy o‘quv yilida o‘zlashtirish ko‘rsatkichi bo‘yicha GPA
            ko‘rsatkichi 3.5 va undan yuqori bo‘lishi talab etiladi" degan talablarga ko‘ra,
            GPA ko‘rsatkichi 3.5 dan kam bo‘lganligi sababli, Oliy ta’lim tashkilotlarida
            talabalarga grantlarni taqdim etish va qayta taqsimlash bo‘yicha tanlovda ishtirok eta olmaysiz.
        </div>

        <div class="footer" style="color: red">
            Sana: {datetime.now().strftime('%Y-%m-%d')}
        </div>
    </body>
    </html>
    """

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    HTML(string=html).write_pdf(filepath)


def generate_acceptance_pdf(filepath, user, gpa):
    academic_score = gpa * 16
    current_time = datetime.now().strftime('%Y-%m-%d')
    
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
           <b> Hurmatli {user.full_name}! </b>
        </div>

        <div class="content" >
            Sizning GPA balingiz {gpa}. <br/>
            Siz Oliy ta’lim tashkilotlarida talabalarga grantlarni taqdim etish va qayta taqsimlash bo‘yicha tanlovda ishtirok etdingiz.<br/>
            Akademik o‘zlashtirish ko‘rsatkichingiz: {academic_score}.
           
        </div>

        <div class="footer" style="color: red">
            Sana: {current_time}
        </div>
    </body>
    </html>
    """

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    HTML(string=html).write_pdf(filepath)



def generate_filename(prefix="file", extension="txt"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # 20250623_1904
    unique_id = uuid.uuid4().hex[:6]  # e.g., a1b2c3
    filename = f"{prefix}_{timestamp}_{unique_id}.{extension}"
    return filename
