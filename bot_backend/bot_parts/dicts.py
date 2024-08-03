from random import randint


def get_lang_greet_text(user_first_name):
    """
    Generates a greeting for the user depending on the random value,
    most often gives a normal greeting.
    :param user_first_name:
    :return: Text greeting in a random language
    """

    lang_greet_dict = {
        54: f'<b>Да пребудет с тобой сила, '
            f'<u>{user_first_name}!</u> \U0001F47D'
            f'Помочь вам могу я чем?</b>',
        900: f'<b>?ьчомоп мав угом я меч, '
             f'<u>{user_first_name[::-1]}</u></b> \U0001F643',
        901: f'<b>नमस्ते <u>{user_first_name}</u>, '
             f'मैं आपकी कैसे मदद कर सकता हूँ?</b> \U0001F642',
        902: f'<b>Greetings <u>{user_first_name}</u>, '
             f'how can I help you?</b> \U0001F642',
        903: f'<b>¡Hola! <u>{user_first_name}</u>, '
             f'¿le puedo ayudar en algo?</b> \U0001F642',
        904: f'<b>你好 <u>{user_first_name}</u>, '
             f'我怎么帮你？</b> \U0001F642',
        906: f'<b>مرحبا <u>{user_first_name}</u>, كيف يمكنني مساعدتك؟'
             f'</b> \U0001F642',
        907: f'<b>Merhaba <u>{user_first_name}</u>, '
             f'nasıl yardımcı olabilirim?</b> \U0001F642',
        908: f'<b>Konnichiwa <u>{user_first_name}</u>, '
             f'dou tasukeraremasuka?</b> \U0001F642',
        909: f'<b>Hallo <u>{user_first_name}</u>, '
             f'wie kann ich Ihnen helfen?</b> \U0001F642',
        910: f'<b>Bonjour <u>{user_first_name}</u>, '
             f'comment puis-je vous aider?</b> \U0001F642',
        911: f'<b>Ciao <u>{user_first_name}</u>, '
             f'come posso aiutarti?</b> \U0001F642',
        912: f'<b>Szia <u>{user_first_name}</u>, '
             f'hogyan segíthetek?</b> \U0001F642',
        913: f'<b>Olá <u>{user_first_name}</u>, '
             f'como posso ajudar?</b> \U0001F642',
        914: f'<b>Hej <u>{user_first_name}</u>, '
             f'hur kan jag hjälpa dig?</b> \U0001F642',
        915: f'<b>Saluton <u>{user_first_name}</u>, '
             f'kiel mi povas helpi vin?</b> \U0001F642',
        916: f'<b>Rytsas, <u>{user_first_name}</u>, '
             f'skorkydoso kostagon nyke dohaeragon ao?</b> \U0001F642',
        917: f'<b>Sveiki <u>{user_first_name}</u>, '
             f'kaip galiu jums padėti?</b> \U0001F642',
        918: f'<b>Բարև <u>{user_first_name}</u>, '
             f'ինչպես կարող եմ օգնել ձեզ?</b> \U0001F642',
        919: f'<b>Sawubona <u>{user_first_name}</u>, '
             f'ngicela ngingakusiza njani?</b> \U0001F642',
        920: f'<b>Γειά σας <u>{user_first_name}</u>, '
             f'πώς μπορώ να σε βοηθήσω?</b> \U0001F642',
        'default': f'<b><u>{user_first_name}</u>, '
                   f'чем я могу вам помочь?</b> \U0001F642'
    }

    lang = randint(1, 1000)
    return lang_greet_dict.get(
        lang,
        lang_greet_dict['default']
    )
