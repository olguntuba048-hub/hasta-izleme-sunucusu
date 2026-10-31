# Hasta İzleme Bulut Sunucusu
FastAPI prototipi: web paneli `/`, sağlık kontrolü `/health`, olay gönderme `POST /api/events`, olay listesi `GET /api/events`, canlı panel WebSocket `/ws`.

Render'a dağıtım: Bu klasörü GitHub deposuna yükleyin, Render'da New + > Web Service ile depoyu bağlayın. `render.yaml` yapılandırması kullanılabilir. Render ortam değişkeni `EVENT_API_KEY` otomatik oluşturulur. Spyder isteklerinde bu anahtarı `X-API-Key` başlığında gönderin.

Spyder örneği:
```python
import requests
requests.post("https://SERVIS-ADIN.onrender.com/api/events",
 json={"room_id":"ODA-01","event_type":"test_event","risk_level":"bilgi","message":"Deneme sinyali","source":"spyder"},
 headers={"X-API-Key":"RENDER_DAN_ALINAN_ANAHTAR"},timeout=20)
```
Bu prototip tıbbi teşhis yapmaz. Render ücretsiz hizmetleri uykuya geçebilir. Ücretsiz hizmetin dosya sistemi kalıcı veri garantisi vermez; kalıcı kayıt için kalıcı disk/veritabanı gerekir. Mobil uygulamaya arka planda bildirim göndermek için ayrıca Expo Push/FCM entegrasyonu yapılmalıdır.
