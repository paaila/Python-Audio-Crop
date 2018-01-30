generate: MainWindow.py
%.py:%.ui
	pyuic5 $<  > $@

clean:
	rm -rf MainWindow.py
remake:clean generate


