from setuptools import setup

setup(
    name='ScreenRecord',
    version='0.1.2',
    packages=['recording_tools', 'recording_tools.closable_server', 'recording_tools.recording_service',
              'telegram_tools', 'imaging_tools'],
    url='',
    license='',
    author='James Kai',
    author_email='kai.hsiang.ju@gmail.com',
    install_requires=[
        "setuptools ~= 52.0.0",
        "rpyc ~= 5.0.1",
        "pyautogui ~= 0.9.52",
        "opencv-python ~= 4.2",
        "numpy",
        "python-telegram-bot ~= 13.2",
        "cnocr"]
)
