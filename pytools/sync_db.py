
import os
import traceback

import pymongo
from py_snippets.saver import Saver

mongodb_uri = os.environ.get('MONGODB_URI_LD')


def sync(db_path='./static/database.db', force_download=False, update_list=None):
    for _ in range(3):
        try:
            with pymongo.MongoClient(mongodb_uri) as client:
                collection = client.heroku_ggpxscwz.article
                update_list = update_list or []
                yield 'start sync db... \nforce_download: %s; update_list: %s' % (
                    bool(force_download), len(update_list))
                DB = Saver(db_path, mode='sqlitedict')
                if update_list:
                    # yield '%s docs need to update urls' % len(update_list)
                    preview_titles = [i['title'] for i in update_list][:5]
                    for item in update_list:
                        collection.update_one({'_id': item['_id']}, {
                                              '$set': item}, upsert=True)
                    yield '%s update_list finished...\n%s' % (len(update_list), preview_titles)
                    return
                if force_download:
                    yield 'force_download only...'
                    mongo_docs = list(collection.find())
                    DB['article'] = sorted(mongo_docs, key=lambda x: x[
                                           'time'], reverse=True)
                    yield 'force_download ok.'
                else:
                    local_docs = DB['article']
                    mongo_docs = list(collection.find())
                    local_len = len(local_docs)
                    mongo_len = len(mongo_docs)
                    if local_len > mongo_len:
                        cmp = '==>'
                    elif local_len == mongo_len:
                        cmp = '==='
                    else:
                        cmp = '<=='
                    yield '%s %s %s %s %s' % (local_len, 'local_docs', cmp, mongo_len, 'mongo_docs')
                    mongo_ids = {i['_id'] for i in mongo_docs}
                    local_ids = {i['_id'] for i in local_docs}
                    # upload
                    to_upload = [i for i in local_docs if i[
                        '_id'] in local_ids - mongo_ids]
                    to_download = [i for i in mongo_docs if i[
                        '_id'] in mongo_ids - local_ids]
                    yield '%s  %s; %s  %s' % (len(to_upload), 'to be uploaded...', len(to_download), 'to be downloaded...')
                    if to_upload:
                        # yield 'uploading'
                        collection.insert_many(to_upload)
                    # yield '%s  %s' % (len(to_upload), 'uploaded...')
                    # download
                    if to_download:
                        # yield 'downloading'
                        DB['article'] = sorted(
                            local_docs + to_download, key=lambda x: x['time'],
                            reverse=True)
                    # yield '%s  %s' % (len(to_download), 'downloaded...')

                yield '============== sync_db finished =============='
                return
        except:
            yield traceback.format_exc()


if __name__ == '__main__':
    for i in sync('E:\github\database.db'):
        print(i)
    os.system('pause')