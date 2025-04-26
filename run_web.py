import uvicorn
import main

if __name__ == '__main__':
    uvicorn.run(app=main.main, port=8000, host='localhost', use_colors=True, log_config=None)
