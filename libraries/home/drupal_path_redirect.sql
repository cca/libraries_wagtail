SELECT source as old_path,
    IF(query != '', CONCAT(redirect, '?', query), redirect) as redirect_link
FROM path_redirect
