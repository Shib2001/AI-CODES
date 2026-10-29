# RAG ka Async Flow

Simple words mein: API user ka question leti hai, uska kaam queue mein bhejti
hai, aur turant ek `job_id` de deti hai. Worker background mein answer banata
hai. Isliye user ko answer ke liye API request khatam hone tak wait nahi karna
padta.

## Ek question ka safar

1. **User question bhejta hai**  
   Client `POST /chat?query=...` request [server.py](./server.py) ko bhejta hai.

2. **API job queue mein daalti hai**  
   FastAPI `process_query` aur question ko RQ queue mein bhejti hai. Valkey is
   job ko temporarily store karta hai. API user ko `job_id` dekar response kar
   deti hai; abhi final answer nahi aata.

3. **Worker job uthata hai**  
   Alag se chalta hua RQ worker `default` queue se job uthata hai aur
   [worker.py](./queues/worker.py) ka `process_query` function chalata hai.

4. **RAG answer banata hai**  
   Worker OpenRouter se question ka embedding banwata hai, Qdrant mein milte-julte
   PDF chunks dhoondhta hai, aur un chunks ko OpenRouter ke chat model ko bhejta
   hai. Model ka answer worker ko milta hai.

5. **Answer job ke saath save hota hai**  
   RQ answer ko job result ke roop mein Valkey mein rakhta hai.

6. **User result check karta hai**  
   Client `GET /job-status?job_id=...` bhejkar result leta hai. Agar job abhi
   chal rahi ho, result filhaal `null` ho sakta hai; baad mein dobara check karein.

## Chhota diagram

```text
User --question--> FastAPI
                    |
                    | job + job_id
                    v
                  Valkey  <-- Worker job uthata hai
                              |
                              +--> OpenRouter: question embedding
                              +--> Qdrant: related PDF chunks
                              +--> OpenRouter: final answer
                              |
                              +--> Answer job result mein save

User --job_id se result poochta hai--> FastAPI --> Valkey se result
```

## Kaun kya karta hai?

- **FastAPI**: request leti hai, job queue karti hai, aur result deti hai.
- **Valkey**: pending jobs aur RQ ke job results rakhta hai.
- **RQ worker**: queue se job uthakar RAG ka kaam karta hai. Worker alag
  terminal/process mein chalta rehna chahiye.
- **Qdrant**: PDF ke pehle se indexed chunks aur unke vectors rakhta hai.
- **OpenRouter**: question embedding aur chat answer provide karta hai.

## Simple RAG ke comparison mein async flow kyun?

Simple RAG mein `chat.py` ek hi process mein question search karta hai, model se
answer leta hai, aur phir answer print karta hai. Jab tak search aur model ka
kaam khatam nahi hota, program wait karta hai.

Async version mein FastAPI question ko Valkey queue mein daal kar `job_id`
jaldi return kar deti hai. Worker alag process mein RAG ka kaam karta hai;
client baad mein `job_id` se result check karta hai.

Isse fayda:

- **API jaldi response deti hai**: user ko lambi model request ke dauran
  connection khula rakhne ki zaroorat nahi.
- **Slow kaam background mein hota hai**: API request aur RAG processing
  alag-alag rehte hain.
- **Zyada requests sambhalna aasaan hota hai**: queue jobs ko line mein rakhti
  hai, aur zaroorat par additional workers chala sakte hain.
- **Temporary load manage hota hai**: ek saath aaye jobs queue mein wait karte
  hain, API par sab kaam ek hi waqt mein nahi hota.

Lekin async setup mein Valkey aur worker bhi chalne chahiye. Simple RAG chhota
experiment ya local test ke liye aasaan hai; queue wala flow lamba chalne wala
API ya slow jobs ke liye zyada practical hai. Abhi client ko answer ke liye
`/job-status` dobara call karna padta hai; automatic notification abhi nahi hai.

## Chalane ke commands

Repository root `C:\Users\Admin\AI-CODES` se API chalayen:

```powershell
python -m uvicorn RAG_QUEUES.server:app --reload --host 127.0.0.1 --port 8000
```

Worker ko ek doosre terminal mein repository root se chalayen. Windows par
default RQ worker `fork()` use nahi kar sakta, isliye `SimpleWorker` use karein:

```powershell
rq worker --worker-class rq.worker.SimpleWorker default
```

Saath mein Valkey (`localhost:6379`) aur Qdrant (`localhost:6333`) bhi chalne
chahiye. Worker ko OpenRouter key `.env` se milti hai.

## Yaad rakhein

- `job_id` milne ka matlab hai request queue hui hai; iska matlab yeh nahi ki
  answer ready hai.
- Abhi `/job-status` result return karta hai; queued/running ka clear status
  nahi deta.
- API aur worker alag processes hain. Dono ko wahi Python environment use karna
  chahiye, aur worker ko `default` queue sunni chahiye.
