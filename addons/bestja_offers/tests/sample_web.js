// PhantomArg: url_path = /web
// PhantomArg: login = administrator

// This doesn't work - topbar name is empty initially.
// We should figure out how to wait when the backend is loaded.
assert($(".oe_topbar_name").text() == "Administrator");
