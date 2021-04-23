window.onload = function () {
    if (document.getElementById('story')) {
        autoSave()
        if (!('emoji' in $.cookie(''))) {
            refreshEmoji();
        } else {
            document.getElementById('emoji_str').innerHTML = $.cookie('emoji');
        }
    }
}


function autoSave() {
    const story_cache = document.getElementById('story').value;
    const input_length = story_cache.length;
    $.cookie('tempstory', story_cache);
    const word_count = document.getElementById('word_count')
    word_count.textContent = input_length + '/' + '500'
    if (input_length > 500) {
        word_count.setAttribute('class', 'col text-end text-danger')
    } else {
        word_count.setAttribute('class', 'col text-end text-muted')
    }
}


function likePost(post) {
    const csrftoken = document.getElementById("csrf_token").getAttribute('value');
    const post_id = post.parentElement.getAttribute('id')
    $.ajax({
            type: 'POST',
            url: like_url,
            data: JSON.stringify({post_id: post_id}),
            contentType: 'application/json',
            dataType: 'json',
            headers: {"X-CSRFToken": csrftoken},
            success: function (data) {
                let likes_node = post.getElementsByTagName('text')[0].firstChild;
                let icon_node = post.getElementsByTagName('i')[0];
                let likes = Number(likes_node.nodeValue);
                if (data.result === 'unlike') {
                    likes -= 1;
                    icon_node.setAttribute('class', "bi bi-hand-thumbs-up");
                } else {
                    likes += 1;
                    icon_node.setAttribute('class', "bi bi-hand-thumbs-up-fill text-danger");
                }
                likes_node.nodeValue = ' ' + likes.toString();
            },
            error: function (e) {
                alert('Log in to give it a thumb up!')
            }
        }
    )
    return false
}


function refreshEmoji() {
    const csrftoken = document.getElementById("csrf_token").getAttribute('value');
    $.ajax({
            type: 'POST',
            url: refresh_url,
            headers: {"X-CSRFToken": csrftoken},
            dataType: 'json',
            success: function (data) {
                const new_emoji = data.emoji_str;
                document.getElementById('emoji_str').innerHTML = new_emoji;
                document.cookie = "emoji=" + new_emoji;
            }
        }
    )
    return false
}
