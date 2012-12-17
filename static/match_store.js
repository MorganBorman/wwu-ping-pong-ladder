var matchStore = null;

require(["dojo/data/ObjectStore", "dojo/store/JsonRest"], function(ObjectStore, JsonRest) {
    var store = new JsonRest({
        target: "/Leaderboard/Match-History/data/"
    });
	
	matchStore = new ObjectStore({objectStore: store});
});
