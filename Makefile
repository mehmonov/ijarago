ssh:
	ssh root@94.198.217.12

go:
	git add .
	git commit -m "update"
	git push origin main

deploy:
	make go
	make ssh