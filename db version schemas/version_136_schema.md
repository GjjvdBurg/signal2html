.schema
CREATE TABLE sms (_id INTEGER PRIMARY KEY AUTOINCREMENT, thread_id INTEGER, address INTEGER, address_device_id INTEGER DEFAULT 1, person INTEGER, date INTEGER, date_sent INTEGER, date_server INTEGER DEFAULT -1, protocol INTEGER, read INTEGER DEFAULT 0, status INTEGER DEFAULT -1,type INTEGER, reply_path_present INTEGER, delivery_receipt_count INTEGER DEFAULT 0,subject TEXT, body TEXT, mismatched_identities TEXT DEFAULT NULL, service_center TEXT, subscription_id INTEGER DEFAULT -1, expires_in INTEGER DEFAULT 0, expire_started INTEGER DEFAULT 0, notified DEFAULT 0, read_receipt_count INTEGER DEFAULT 0, unidentified INTEGER DEFAULT 0, reactions_unread INTEGER DEFAULT 0, reactions_last_seen INTEGER DEFAULT -1, remote_deleted INTEGER DEFAULT 0, notified_timestamp INTEGER DEFAULT 0, server_guid TEXT DEFAULT NULL, receipt_timestamp INTEGER DEFAULT -1, export_state BLOB DEFAULT NULL, exported INTEGER DEFAULT 0);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE mms (_id INTEGER PRIMARY KEY AUTOINCREMENT, thread_id INTEGER, date INTEGER, date_received INTEGER, date_server INTEGER DEFAULT -1, msg_box INTEGER, read INTEGER DEFAULT 0, body TEXT, part_count INTEGER, ct_l TEXT, address INTEGER, address_device_id INTEGER, exp INTEGER, m_type INTEGER, m_size INTEGER, st INTEGER, tr_id TEXT, delivery_receipt_count INTEGER DEFAULT 0, mismatched_identities TEXT DEFAULT NULL, network_failures TEXT DEFAULT NULL,subscription_id INTEGER DEFAULT -1, expires_in INTEGER DEFAULT 0, expire_started INTEGER DEFAULT 0, notified INTEGER DEFAULT 0, read_receipt_count INTEGER DEFAULT 0, quote_id INTEGER DEFAULT 0, quote_author TEXT, quote_body TEXT, quote_attachment INTEGER DEFAULT -1, quote_missing INTEGER DEFAULT 0, quote_mentions BLOB DEFAULT NULL,shared_contacts TEXT, unidentified INTEGER DEFAULT 0, previews TEXT, reveal_duration INTEGER DEFAULT 0, reactions_unread INTEGER DEFAULT 0, reactions_last_seen INTEGER DEFAULT -1, remote_deleted INTEGER DEFAULT 0, mentions_self INTEGER DEFAULT 0, notified_timestamp INTEGER DEFAULT 0, viewed_receipt_count INTEGER DEFAULT 0, server_guid TEXT DEFAULT NULL, receipt_timestamp INTEGER DEFAULT -1, ranges BLOB DEFAULT NULL, is_story INTEGER DEFAULT 0, parent_story_id INTEGER DEFAULT 0, quote_type INTEGER DEFAULT 0, export_state BLOB DEFAULT NULL, exported INTEGER DEFAULT 0);
CREATE TABLE part (_id INTEGER PRIMARY KEY, mid INTEGER, seq INTEGER DEFAULT 0, ct TEXT, name TEXT, chset INTEGER, cd TEXT, fn TEXT, cid TEXT, cl TEXT, ctt_s INTEGER, ctt_t TEXT, encrypted INTEGER, pending_push INTEGER, _data TEXT, data_size INTEGER, file_name TEXT, unique_id INTEGER NOT NULL, digest BLOB, fast_preflight_id TEXT, voice_note INTEGER DEFAULT 0, borderless INTEGER DEFAULT 0, video_gif INTEGER DEFAULT 0, data_random BLOB, quote INTEGER DEFAULT 0, width INTEGER DEFAULT 0, height INTEGER DEFAULT 0, caption TEXT DEFAULT NULL, sticker_pack_id TEXT DEFAULT NULL, sticker_pack_key DEFAULT NULL, sticker_id INTEGER DEFAULT -1, sticker_emoji STRING DEFAULT NULL, data_hash TEXT DEFAULT NULL, blur_hash TEXT DEFAULT NULL, transform_properties TEXT DEFAULT NULL, transfer_file TEXT DEFAULT NULL, display_order INTEGER DEFAULT 0, upload_timestamp INTEGER DEFAULT 0, cdn_number INTEGER DEFAULT 0);
CREATE TABLE thread (_id INTEGER PRIMARY KEY AUTOINCREMENT, date INTEGER DEFAULT 0, message_count INTEGER DEFAULT 0, thread_recipient_id INTEGER, snippet TEXT, snippet_charset INTEGER DEFAULT 0, read INTEGER DEFAULT 1, type INTEGER DEFAULT 0, error INTEGER DEFAULT 0, snippet_type INTEGER DEFAULT 0, snippet_uri TEXT DEFAULT NULL, snippet_content_type TEXT DEFAULT NULL, snippet_extras TEXT DEFAULT NULL, archived INTEGER DEFAULT 0, status INTEGER DEFAULT 0, delivery_receipt_count INTEGER DEFAULT 0, expires_in INTEGER DEFAULT 0, last_seen INTEGER DEFAULT 0, has_sent INTEGER DEFAULT 0, read_receipt_count INTEGER DEFAULT 0, unread_count INTEGER DEFAULT 0, last_scrolled INTEGER DEFAULT 0, pinned INTEGER DEFAULT 0, unread_self_mention_count INTEGER DEFAULT 0);
CREATE TABLE identities (_id INTEGER PRIMARY KEY AUTOINCREMENT, address INTEGER UNIQUE, identity_key TEXT, first_use INTEGER DEFAULT 0, timestamp INTEGER DEFAULT 0, verified INTEGER DEFAULT 0, nonblocking_approval INTEGER DEFAULT 0);
CREATE TABLE drafts (_id INTEGER PRIMARY KEY, thread_id INTEGER, type TEXT, value TEXT);
CREATE TABLE push (_id INTEGER PRIMARY KEY, type INTEGER, source TEXT, source_uuid TEXT, device_id INTEGER, body TEXT, content TEXT, timestamp INTEGER, server_timestamp INTEGER DEFAULT 0, server_delivered_timestamp INTEGER DEFAULT 0, server_guid TEXT DEFAULT NULL);
CREATE TABLE groups (_id INTEGER PRIMARY KEY, group_id TEXT, recipient_id INTEGER, title TEXT, members TEXT, avatar_id INTEGER, avatar_key BLOB, avatar_content_type TEXT, avatar_relay TEXT, timestamp INTEGER, active INTEGER DEFAULT 1, avatar_digest BLOB, mms INTEGER DEFAULT 0, master_key BLOB, revision BLOB, decrypted_group BLOB, expected_v2_id TEXT DEFAULT NULL, former_v1_members TEXT DEFAULT NULL, distribution_id TEXT DEFAULT NULL, display_as_story INTEGER DEFAULT 0, auth_service_id TEXT DEFAULT NULL, last_force_update_timestamp INTEGER DEFAULT 0);
CREATE TABLE recipient (
  _id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT UNIQUE DEFAULT NULL,
  username TEXT UNIQUE DEFAULT NULL,
  phone TEXT UNIQUE DEFAULT NULL,
  email TEXT UNIQUE DEFAULT NULL,
  group_id TEXT UNIQUE DEFAULT NULL,
  group_type INTEGER DEFAULT 0,
  blocked INTEGER DEFAULT 0,
  message_ringtone TEXT DEFAULT NULL, 
  message_vibrate INTEGER DEFAULT 0, 
  call_ringtone TEXT DEFAULT NULL, 
  call_vibrate INTEGER DEFAULT 0, 
  notification_channel TEXT DEFAULT NULL, 
  mute_until INTEGER DEFAULT 0, 
  color TEXT DEFAULT NULL, 
  seen_invite_reminder INTEGER DEFAULT 0,
  default_subscription_id INTEGER DEFAULT -1,
  message_expiration_time INTEGER DEFAULT 0,
  registered INTEGER DEFAULT 0,
  system_given_name TEXT DEFAULT NULL, 
  system_family_name TEXT DEFAULT NULL, 
  system_display_name TEXT DEFAULT NULL, 
  system_photo_uri TEXT DEFAULT NULL, 
  system_phone_label TEXT DEFAULT NULL, 
  system_phone_type INTEGER DEFAULT -1, 
  system_contact_uri TEXT DEFAULT NULL, 
  system_info_pending INTEGER DEFAULT 0, 
  profile_key TEXT DEFAULT NULL, 
  profile_key_credential TEXT DEFAULT NULL, 
  signal_profile_name TEXT DEFAULT NULL, 
  profile_family_name TEXT DEFAULT NULL, 
  profile_joined_name TEXT DEFAULT NULL, 
  signal_profile_avatar TEXT DEFAULT NULL, 
  profile_sharing INTEGER DEFAULT 0, 
  last_profile_fetch INTEGER DEFAULT 0, 
  unidentified_access_mode INTEGER DEFAULT 0, 
  force_sms_selection INTEGER DEFAULT 0, 
  storage_service_key TEXT UNIQUE DEFAULT NULL, 
  mention_setting INTEGER DEFAULT 0, 
  storage_proto TEXT DEFAULT NULL,
  capabilities INTEGER DEFAULT 0,
  last_session_reset BLOB DEFAULT NULL,
  wallpaper BLOB DEFAULT NULL,
  wallpaper_file TEXT DEFAULT NULL,
  about TEXT DEFAULT NULL,
  about_emoji TEXT DEFAULT NULL,
  extras BLOB DEFAULT NULL,
  groups_in_common INTEGER DEFAULT 0,
  chat_colors BLOB DEFAULT NULL,
  custom_chat_colors_id INTEGER DEFAULT 0,
  badges BLOB DEFAULT NULL,
  pni TEXT DEFAULT NULL,
  distribution_list_id INTEGER DEFAULT NULL
, needs_pni_signature, unregistered_timestamp INTEGER DEFAULT 0, hidden INTEGER DEFAULT 0);
CREATE TABLE group_receipts (_id INTEGER PRIMARY KEY, mms_id INTEGER, address INTEGER, status INTEGER, timestamp INTEGER, unidentified INTEGER DEFAULT 0);
CREATE TABLE one_time_prekeys (
        _id INTEGER PRIMARY KEY,
        account_id TEXT NOT NULL,
        key_id INTEGER UNIQUE, 
        public_key TEXT NOT NULL, 
        private_key TEXT NOT NULL,
        UNIQUE(account_id, key_id)
      );
CREATE TABLE signed_prekeys (
        _id INTEGER PRIMARY KEY,
        account_id TEXT NOT NULL,
        key_id INTEGER UNIQUE, 
        public_key TEXT NOT NULL,
        private_key TEXT NOT NULL,
        signature TEXT NOT NULL, 
        timestamp INTEGER DEFAULT 0,
        UNIQUE(account_id, key_id)
    );
CREATE TABLE sessions (
        _id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id TEXT NOT NULL,
        address TEXT NOT NULL,
        device INTEGER NOT NULL,
        record BLOB NOT NULL,
        UNIQUE(account_id, address, device)
      );
CREATE TABLE sender_keys(_id INTEGER PRIMARY KEY AUTOINCREMENT, address TEXT NOT NULL, device INTEGER NOT NULL, distribution_id TEXT NOT NULL, record BLOB NOT NULL, created_at INTEGER NOT NULL, UNIQUE(address,device, distribution_id) ON CONFLICT REPLACE);
CREATE TABLE sender_key_shared(_id INTEGER PRIMARY KEY AUTOINCREMENT, distribution_id TEXT NOT NULL, address TEXT NOT NULL, device INTEGER NOT NULL, timestamp INTEGER DEFAULT 0, UNIQUE(distribution_id,address, device) ON CONFLICT REPLACE);
CREATE TABLE pending_retry_receipts(_id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT NOT NULL, device INTEGER NOT NULL, sent_timestamp INTEGER NOT NULL, received_timestamp TEXT NOT NULL, thread_id INTEGER NOT NULL, UNIQUE(author,sent_timestamp) ON CONFLICT REPLACE);
CREATE TABLE sticker (_id INTEGER PRIMARY KEY AUTOINCREMENT, pack_id TEXT NOT NULL, pack_key TEXT NOT NULL, pack_title TEXT NOT NULL, pack_author TEXT NOT NULL, sticker_id INTEGER, cover INTEGER, pack_order INTEGER, emoji TEXT NOT NULL, content_type TEXT DEFAULT NULL, last_used INTEGER, installed INTEGER,file_path TEXT NOT NULL, file_length INTEGER, file_random BLOB, UNIQUE(pack_id, sticker_id, cover) ON CONFLICT IGNORE);
CREATE TABLE storage_key (_id INTEGER PRIMARY KEY AUTOINCREMENT, type INTEGER, key TEXT UNIQUE);
CREATE TABLE mention(_id INTEGER PRIMARY KEY AUTOINCREMENT, thread_id INTEGER, message_id INTEGER, recipient_id INTEGER, range_start INTEGER, range_length INTEGER);
CREATE TABLE payments(_id INTEGER PRIMARY KEY, uuid TEXT DEFAULT NULL, recipient INTEGER DEFAULT 0, recipient_address TEXT DEFAULT NULL, timestamp INTEGER, note TEXT DEFAULT NULL, direction INTEGER, state INTEGER, failure_reason INTEGER, amount BLOB NOT NULL, fee BLOB NOT NULL, transaction_record BLOB DEFAULT NULL, receipt BLOB DEFAULT NULL, payment_metadata BLOB DEFAULT NULL, receipt_public_key TEXT DEFAULT NULL, block_index INTEGER DEFAULT 0, block_timestamp INTEGER DEFAULT 0, seen INTEGER, UNIQUE(uuid) ON CONFLICT ABORT);
CREATE TABLE chat_colors (
  _id INTEGER PRIMARY KEY AUTOINCREMENT,
  chat_colors BLOB
);
CREATE VIRTUAL TABLE emoji_search USING fts5(label, emoji UNINDEXED)
/* emoji_search(label,emoji) */;
CREATE TABLE IF NOT EXISTS 'emoji_search_data'(id INTEGER PRIMARY KEY, block BLOB);
CREATE TABLE IF NOT EXISTS 'emoji_search_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS 'emoji_search_content'(id INTEGER PRIMARY KEY, c0, c1);
CREATE TABLE IF NOT EXISTS 'emoji_search_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE IF NOT EXISTS 'emoji_search_config'(k PRIMARY KEY, v) WITHOUT ROWID;
CREATE TABLE avatar_picker (
  _id INTEGER PRIMARY KEY AUTOINCREMENT,
  last_used INTEGER DEFAULT 0,
  group_id TEXT DEFAULT NULL,
  avatar BLOB NOT NULL
);
CREATE TABLE group_call_ring (
  _id INTEGER PRIMARY KEY,
  ring_id INTEGER UNIQUE,
  date_received INTEGER,
  ring_state INTEGER
);
CREATE TABLE reaction (
  _id INTEGER PRIMARY KEY,
  message_id INTEGER NOT NULL,
  is_mms INTEGER NOT NULL,
  author_id INTEGER NOT NULL REFERENCES recipient (_id) ON DELETE CASCADE,
  emoji TEXT NOT NULL,
  date_sent INTEGER NOT NULL,
  date_received INTEGER NOT NULL,
  UNIQUE(message_id, is_mms, author_id) ON CONFLICT REPLACE
);
CREATE TABLE donation_receipt (
  _id INTEGER PRIMARY KEY AUTOINCREMENT,
  receipt_type TEXT NOT NULL,
  receipt_date INTEGER NOT NULL,
  amount TEXT NOT NULL,
  currency TEXT NOT NULL,
  subscription_level INTEGER NOT NULL
);
CREATE VIRTUAL TABLE sms_fts USING fts5(body, thread_id UNINDEXED, content=sms, content_rowid=_id)
/* sms_fts(body,thread_id) */;
CREATE TABLE IF NOT EXISTS 'sms_fts_data'(id INTEGER PRIMARY KEY, block BLOB);
CREATE TABLE IF NOT EXISTS 'sms_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS 'sms_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE IF NOT EXISTS 'sms_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;
CREATE TRIGGER sms_ai AFTER INSERT ON sms BEGIN
  INSERT INTO sms_fts(rowid, body, thread_id) VALUES (new._id, new.body, new.thread_id);
END;
CREATE TRIGGER sms_ad AFTER DELETE ON sms BEGIN
  INSERT INTO sms_fts(sms_fts, rowid, body, thread_id) VALUES('delete', old._id, old.body, old.thread_id);
END;
CREATE TRIGGER sms_au AFTER UPDATE ON sms BEGIN
  INSERT INTO sms_fts(sms_fts, rowid, body, thread_id) VALUES('delete', old._id, old.body, old.thread_id);
  INSERT INTO sms_fts(rowid, body, thread_id) VALUES(new._id, new.body, new.thread_id);
END;
CREATE VIRTUAL TABLE mms_fts USING fts5(body, thread_id UNINDEXED, content=mms, content_rowid=_id)
/* mms_fts(body,thread_id) */;
CREATE TABLE IF NOT EXISTS 'mms_fts_data'(id INTEGER PRIMARY KEY, block BLOB);
CREATE TABLE IF NOT EXISTS 'mms_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS 'mms_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE IF NOT EXISTS 'mms_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;
CREATE TRIGGER mms_ai AFTER INSERT ON mms BEGIN
  INSERT INTO mms_fts(rowid, body, thread_id) VALUES (new._id, new.body, new.thread_id);
END;
CREATE TRIGGER mms_ad AFTER DELETE ON mms BEGIN
  INSERT INTO mms_fts(mms_fts, rowid, body, thread_id) VALUES('delete', old._id, old.body, old.thread_id);
END;
CREATE TRIGGER mms_au AFTER UPDATE ON mms BEGIN
  INSERT INTO mms_fts(mms_fts, rowid, body, thread_id) VALUES('delete', old._id, old.body, old.thread_id);
  INSERT INTO mms_fts(rowid, body, thread_id) VALUES (new._id, new.body, new.thread_id);
END;
CREATE TABLE remapped_recipients (_id INTEGER PRIMARY KEY AUTOINCREMENT, old_id INTEGER UNIQUE, new_id INTEGER);
CREATE TABLE remapped_threads (_id INTEGER PRIMARY KEY AUTOINCREMENT, old_id INTEGER UNIQUE, new_id INTEGER);
CREATE TABLE msl_payload (
        _id INTEGER PRIMARY KEY,
        date_sent INTEGER NOT NULL,
        content BLOB NOT NULL,
        content_hint INTEGER NOT NULL
      , urgent INTEGER NOT NULL DEFAULT 1);
CREATE TABLE msl_recipient (
        _id INTEGER PRIMARY KEY,
        payload_id INTEGER NOT NULL REFERENCES msl_payload (_id) ON DELETE CASCADE,
        recipient_id INTEGER NOT NULL, 
        device INTEGER NOT NULL
      );
CREATE TABLE msl_message (
        _id INTEGER PRIMARY KEY,
        payload_id INTEGER NOT NULL REFERENCES msl_payload (_id) ON DELETE CASCADE,
        message_id INTEGER NOT NULL, 
        is_mms INTEGER NOT NULL
      );
CREATE TABLE notification_profile (
  _id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  emoji TEXT NOT NULL,
  color TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  allow_all_calls INTEGER NOT NULL DEFAULT 0,
  allow_all_mentions INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE notification_profile_schedule (
  _id INTEGER PRIMARY KEY AUTOINCREMENT,
  notification_profile_id INTEGER NOT NULL REFERENCES notification_profile (_id) ON DELETE CASCADE,
  enabled INTEGER NOT NULL DEFAULT 0,
  start INTEGER NOT NULL,
  end INTEGER NOT NULL,
  days_enabled TEXT NOT NULL
);
CREATE TABLE notification_profile_allowed_members (
  _id INTEGER PRIMARY KEY AUTOINCREMENT,
  notification_profile_id INTEGER NOT NULL REFERENCES notification_profile (_id) ON DELETE CASCADE,
  recipient_id INTEGER NOT NULL,
  UNIQUE(notification_profile_id, recipient_id) ON CONFLICT REPLACE
);
CREATE TABLE distribution_list (
        _id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        distribution_id TEXT UNIQUE NOT NULL,
        recipient_id INTEGER UNIQUE REFERENCES recipient (_id),
        allows_replies INTEGER DEFAULT 1
      , deletion_timestamp INTEGER DEFAULT 0, is_unknown INTEGER DEFAULT 0, privacy_mode INTEGER DEFAULT 0);
CREATE INDEX recipient_group_type_index ON recipient (group_type);
CREATE UNIQUE INDEX recipient_pni_index ON recipient (pni);
CREATE INDEX sms_read_and_notified_and_thread_id_index ON sms(read,notified,thread_id);
CREATE INDEX sms_type_index ON sms (type);
CREATE INDEX sms_date_sent_index ON sms (date_sent, address, thread_id);
CREATE INDEX sms_date_server_index ON sms (date_server);
CREATE INDEX sms_thread_date_index ON sms (thread_id, date);
CREATE INDEX sms_reactions_unread_index ON sms (reactions_unread);
CREATE INDEX mms_read_and_notified_and_thread_id_index ON mms(read,notified,thread_id);
CREATE INDEX mms_message_box_index ON mms (msg_box);
CREATE INDEX mms_date_sent_index ON mms (date, address, thread_id);
CREATE INDEX mms_date_server_index ON mms (date_server);
CREATE INDEX mms_thread_date_index ON mms (thread_id, date_received);
CREATE INDEX mms_reactions_unread_index ON mms (reactions_unread);
CREATE INDEX mms_is_story_index ON mms (is_story);
CREATE INDEX mms_parent_story_id_index ON mms (parent_story_id);
CREATE INDEX mms_thread_story_parent_story_index ON mms (thread_id, date_received,is_story,parent_story_id);
CREATE INDEX part_mms_id_index ON part (mid);
CREATE INDEX pending_push_index ON part (pending_push);
CREATE INDEX part_sticker_pack_id_index ON part (sticker_pack_id);
CREATE INDEX part_data_hash_index ON part (data_hash);
CREATE INDEX part_data_index ON part (_data);
CREATE INDEX thread_recipient_id_index ON thread (thread_recipient_id);
CREATE INDEX archived_count_index ON thread (archived, message_count);
CREATE INDEX thread_pinned_index ON thread (pinned);
CREATE INDEX draft_thread_index ON drafts (thread_id);
CREATE UNIQUE INDEX group_id_index ON groups (group_id);
CREATE UNIQUE INDEX group_recipient_id_index ON groups (recipient_id);
CREATE UNIQUE INDEX expected_v2_id_index ON groups (expected_v2_id);
CREATE UNIQUE INDEX group_distribution_id_index ON groups(distribution_id);
CREATE INDEX group_receipt_mms_id_index ON group_receipts (mms_id);
CREATE INDEX sticker_pack_id_index ON sticker (pack_id);
CREATE INDEX sticker_sticker_id_index ON sticker (sticker_id);
CREATE INDEX storage_key_type_index ON storage_key (type);
CREATE INDEX mention_message_id_index ON mention (message_id);
CREATE INDEX mention_recipient_id_thread_id_index ON mention (recipient_id, thread_id);
CREATE INDEX timestamp_direction_index ON payments (timestamp, direction);
CREATE INDEX timestamp_index ON payments (timestamp);
CREATE UNIQUE INDEX receipt_public_key_index ON payments (receipt_public_key);
CREATE INDEX msl_payload_date_sent_index ON msl_payload (date_sent);
CREATE INDEX msl_recipient_recipient_index ON msl_recipient (recipient_id, device, payload_id);
CREATE INDEX msl_recipient_payload_index ON msl_recipient (payload_id);
CREATE INDEX msl_message_message_index ON msl_message (message_id, is_mms, payload_id);
CREATE INDEX date_received_index on group_call_ring (date_received);
CREATE INDEX notification_profile_schedule_profile_index ON notification_profile_schedule (notification_profile_id);
CREATE INDEX notification_profile_allowed_members_profile_index ON notification_profile_allowed_members (notification_profile_id);
CREATE INDEX donation_receipt_type_index ON donation_receipt (receipt_type);
CREATE INDEX donation_receipt_date_index ON donation_receipt (receipt_date);
CREATE TRIGGER msl_sms_delete AFTER DELETE ON sms 
        BEGIN 
        	DELETE FROM msl_payload WHERE _id IN (SELECT payload_id FROM msl_message WHERE message_id = old._id AND is_mms = 0);
        END;
CREATE TRIGGER msl_mms_delete AFTER DELETE ON mms 
        BEGIN 
        	DELETE FROM msl_payload WHERE _id IN (SELECT payload_id FROM msl_message WHERE message_id = old._id AND is_mms = 1);
        END;
CREATE TRIGGER msl_attachment_delete AFTER DELETE ON part
        BEGIN
        	DELETE FROM msl_payload WHERE _id IN (SELECT payload_id FROM msl_message WHERE message_id = old.mid AND is_mms = 1);
        END;
CREATE TRIGGER reactions_sms_delete AFTER DELETE ON sms 
        BEGIN 
        	DELETE FROM reaction WHERE message_id = old._id AND is_mms = 0;
        END;
CREATE TRIGGER reactions_mms_delete AFTER DELETE ON mms 
        BEGIN 
        	DELETE FROM reaction WHERE message_id = old._id AND is_mms = 1;
        END;
CREATE INDEX recipient_service_id_profile_key ON recipient (uuid, profile_key) WHERE uuid NOT NULL AND profile_key NOT NULL;
CREATE TABLE cds (
          _id INTEGER PRIMARY KEY,
          e164 TEXT NOT NULL UNIQUE ON CONFLICT IGNORE,
          last_seen_at INTEGER DEFAULT 0
        );
CREATE TABLE IF NOT EXISTS "story_sends" (
  _id INTEGER PRIMARY KEY,
  message_id INTEGER NOT NULL REFERENCES mms (_id) ON DELETE CASCADE,
  recipient_id INTEGER NOT NULL REFERENCES recipient (_id) ON DELETE CASCADE,
  sent_timestamp INTEGER NOT NULL,
  allows_replies INTEGER NOT NULL,
  distribution_id TEXT NOT NULL REFERENCES distribution_list (distribution_id) ON DELETE CASCADE
);
CREATE INDEX story_sends_recipient_id_sent_timestamp_allows_replies_index ON story_sends (recipient_id, sent_timestamp, allows_replies);
CREATE TABLE remote_megaphone (
            _id INTEGER PRIMARY KEY,
            uuid TEXT UNIQUE NOT NULL,
            priority INTEGER NOT NULL,
            countries TEXT,
            minimum_version INTEGER NOT NULL,
            dont_show_before INTEGER NOT NULL,
            dont_show_after INTEGER NOT NULL,
            show_for_days INTEGER NOT NULL,
            conditional_id TEXT,
            primary_action_id TEXT,
            secondary_action_id TEXT,
            image_url TEXT,
            image_uri TEXT DEFAULT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            primary_action_text TEXT,
            secondary_action_text TEXT,
            shown_at INTEGER DEFAULT 0,
            finished_at INTEGER DEFAULT 0
          , primary_action_data TEXT DEFAULT NULL, secondary_action_data TEXT DEFAULT NULL, snoozed_at INTEGER DEFAULT 0, seen_count INTEGER DEFAULT 0);
CREATE INDEX mms_quote_id_quote_author_index ON mms (quote_id, quote_author);
CREATE TABLE IF NOT EXISTS "distribution_list_member" (
            _id INTEGER PRIMARY KEY AUTOINCREMENT,
            list_id INTEGER NOT NULL REFERENCES distribution_list (_id) ON DELETE CASCADE,
            recipient_id INTEGER NOT NULL REFERENCES recipient (_id),
            privacy_mode INTEGER DEFAULT 0
          );
CREATE UNIQUE INDEX distribution_list_member_list_id_recipient_id_privacy_mode_index ON distribution_list_member (list_id, recipient_id, privacy_mode);
CREATE TABLE pending_pni_signature_message (
  _id INTEGER PRIMARY KEY,
  recipient_id INTEGER NOT NULL REFERENCES recipient (_id) ON DELETE CASCADE,
  sent_timestamp INTEGER NOT NULL,
  device_id INTEGER NOT NULL
);
CREATE UNIQUE INDEX pending_pni_recipient_sent_device_index ON pending_pni_signature_message (recipient_id, sent_timestamp, device_id);
CREATE INDEX sms_exported_index ON sms (exported);
CREATE INDEX mms_exported_index ON mms (exported);
CREATE INDEX story_sends_message_id_distribution_id_index ON story_sends (message_id, distribution_id);
