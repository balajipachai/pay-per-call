"""Sample railway delay notices used by the demo client and tests.

CLEAN_NOTICE is a fully readable notice that should parse and be charged.
Each REJECTED_* notice trips exactly one of the three garbage conditions
the brief calls out: missing/incorrect train number, a past date, and an
unsupported language.
"""

from datetime import date, timedelta

TODAY = date.today().strftime("%d %b %Y")
YESTERDAY = (date.today() - timedelta(days=1)).strftime("%d %b %Y")

CLEAN_NOTICE = f"""Date: {TODAY}
Train Number/Name: 12626 / New Delhi Express
Scheduled Departure/Arrival: 08:15 AM
Status: Delayed
Please be informed that the 12626 New Delhi Express scheduled to depart from Pune to New Delhi is currently running 45 minutes behind schedule due to signalling malfunction.
Estimated Departure Time: 09:00 AM
Platform Number: 3
"""

REJECTED_MISSING_TRAIN_NUMBER = f"""Date: {TODAY}
Train Number/Name: New Delhi Express
Scheduled Departure/Arrival: 08:15 AM
Status: Delayed
Please be informed that the New Delhi Express scheduled to depart from Pune to New Delhi is currently running 45 minutes behind schedule due to signalling malfunction.
Estimated Departure Time: 09:00 AM
Platform Number: 3
"""

REJECTED_PAST_DATE = f"""Date: {YESTERDAY}
Train Number/Name: 12626 / New Delhi Express
Scheduled Departure/Arrival: 08:15 AM
Status: Delayed
Please be informed that the 12626 New Delhi Express scheduled to depart from Pune to New Delhi is currently running 45 minutes behind schedule due to signalling malfunction.
Estimated Departure Time: 09:00 AM
Platform Number: 3
"""

REJECTED_WRONG_LANGUAGE = f"""Date: {TODAY}
Train Number/Name: 12626 / TGV Lyria
Ceci est un avis retardé pour le train numéro 12626 partant de Paris vers Lyon,
actuellement en retard de quarante-cinq minutes en raison d'un problème de signalisation.
Nous nous excusons pour la gêne occasionnée.
"""

HINDI_NOTICE = f"""Date: {TODAY}
Train Number/Name: 12626 / राजधानी एक्सप्रेस
Scheduled Departure/Arrival: 08:15 AM
Status: विलंबित
कृपया ध्यान दें कि 12626 राजधानी एक्सप्रेस, जो पुणे से नई दिल्ली के लिए रवाना होनी थी,
सिग्नल की खराबी के कारण फिलहाल 45 मिनट की देरी से चल रही है। यह सूचना यात्रियों की सुविधा
के लिए स्टेशन प्रशासन द्वारा जारी की गई है ताकि वे अपनी यात्रा की योजना बना सकें।
Please be informed that the 12626 New Delhi Express scheduled to depart from Pune to New Delhi is currently running 45 minutes behind schedule due to signalling malfunction.
Estimated Departure Time: 09:00 AM
Platform Number: 3
"""
