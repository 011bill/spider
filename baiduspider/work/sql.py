insert_zixun = 'INSERT INTO company_bdzixun (id, company, simple_name, title, author, date, ' \
               'des, url, cover, flag, filter, retry, err, remark, collect_date) VALUES ' \
               '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

select_zixun_by_url = 'SELECT * FROM company_bdzixun WHERE url = %s'

insert_company_log = 'INSERT INTO company_log (id, name, status, date) VALUES (%s, %s, %s, %s)'

insert_ban_log = 'INSERT INTO ban_log (id, start_time, end_time, delay, count, date) VALUES (%s, %s, %s, %s, %s, %s)'

