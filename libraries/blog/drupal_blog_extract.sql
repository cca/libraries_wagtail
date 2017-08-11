-- this query extracts the fields from our Drupal 6 blog needed to
-- recreate it in Wagtail
SELECT n.title, REPLACE(a.dst, 'blog/', '') as slug, n.created as date_created, nr.body, f.filepath as main_image
FROM node n
-- connect on the _version_ ID, not node
JOIN node_revisions nr ON n.vid = nr.vid
-- intermediary step to get to files table
LEFT JOIN content_type_blog ctb ON nr.vid = ctb.vid
LEFT JOIN files f ON ctb.field_image_fid = f.fid
LEFT JOIN url_alias a ON CONCAT('node/', n.nid) = a.src
-- presumably status=1 -> published
WHERE n.status = 1 AND n.type = 'blog'
-- limit to the last three years of posts?
AND n.created > 1407628800
ORDER BY n.created DESC
