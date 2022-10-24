from api_server.storage import PostDB, PostData, FoulLanguageStatus


def test_post_db(post_db: PostDB):
    assert len(post_db.posts) == 0

    title0 = "title 0"
    parags0 = ["hello"]

    id0 = post_db.insert_new(PostData(title0, parags0))
    assert id0 == 0
    assert len(post_db.posts) == 1
    assert post_db.posts[0].title == title0
    assert post_db.posts[0].paragraphs == parags0
    assert post_db.posts[0].status == FoulLanguageStatus.PENDING
