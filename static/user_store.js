var userStore = null;

require(["dojo/data/ObjectStore", "dojo/store/JsonRest"], function(ObjectStore, JsonRest) {
    var store = new JsonRest({
        target: "/Leaderboard/users/"
    });
    
    userStore = store;
});
