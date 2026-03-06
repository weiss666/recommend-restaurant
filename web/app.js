const filters = [
  "city",
  "district",
  "hot_spot",
  "avg_price",
  "tags",
  "name",
  "recommended_dishes",
  "source",
  "recent_business_district",
];

const state = {
  userLat: null,
  userLng: null,
  page: 1,
  pageSize: 20,
};

function toTitle(key) {
  const map = {
    city: "城市",
    district: "区",
    hot_spot: "热门地点",
    avg_price: "人均上限",
    tags: "标签",
    name: "店名",
    recommended_dishes: "推荐菜",
    source: "来源",
    recent_business_district: "最近商区",
  };
  return map[key] || key;
}

function fillSelect(id, options, defaultValue = "") {
  const el = document.getElementById(id);
  el.innerHTML = "";
  const all = document.createElement("option");
  all.value = "";
  all.textContent = `${toTitle(id)}(全部)`;
  el.appendChild(all);

  options.forEach((item) => {
    const op = document.createElement("option");
    op.value = String(item);
    op.textContent = String(item);
    el.appendChild(op);
  });

  if (defaultValue) el.value = defaultValue;
}

async function loadFilterOptions() {
  const res = await fetch("./api/filter-options");
  const data = await res.json();

  filters.forEach((key) => {
    fillSelect(key, data[key] || [], key === "city" ? "上海" : "");
  });
}

function buildQuery() {
  const params = new URLSearchParams();
  filters.forEach((key) => {
    const value = document.getElementById(key).value;
    if (value !== "") params.set(key, value);
  });

  const pet = document.getElementById("pet_friendly").value;
  if (pet !== "") params.set("pet_friendly", pet);

  params.set("page", String(state.page));
  params.set("page_size", String(state.pageSize));
  params.set("min_rating", "4.5");

  if (state.userLat != null && state.userLng != null) {
    params.set("user_lat", String(state.userLat));
    params.set("user_lng", String(state.userLng));
  }
  if (!params.get("city")) params.set("city", "上海");
  return params.toString();
}

function renderList(payload) {
  const list = document.getElementById("list");
  list.innerHTML = "";
  const tpl = document.getElementById("cardTemplate");

  payload.items.forEach((item) => {
    const node = tpl.content.cloneNode(true);
    node.querySelector(".name").textContent = item.name;
    node.querySelector(".rating").textContent = `评分 ${item.rating.toFixed(1)}`;
    node.querySelector(".meta").textContent = `${item.city} ${item.district || ""} | 人均 ${item.avg_price || "-"} | ${
      item.hot_spot || "-"
    }`;
    node.querySelector(".tags").textContent = `标签: ${item.tags.join(" / ") || "-"}`;
    node.querySelector(".dishes").textContent = `推荐菜: ${item.recommended_dishes.join(" / ") || "-"}`;
    const distanceText = item.distance_km != null ? `${item.distance_km} km` : "-";
    node.querySelector(
      ".extra"
    ).textContent = `来源: ${item.source} | 宠物友好: ${item.pet_friendly ? "是" : "否"} | 最近商区: ${
      item.recent_business_district || "-"
    } | 距离: ${distanceText}`;
    list.appendChild(node);
  });

  document.getElementById("summary").textContent = `共 ${payload.total} 条，当前第 ${payload.page} 页`;
}

async function loadRestaurants() {
  const res = await fetch(`./api/restaurants?${buildQuery()}`);
  const data = await res.json();
  renderList(data);
}

async function resolveManualLocation() {
  const value = document.getElementById("locationInput").value.trim();
  if (!value) return;
  const res = await fetch(`./api/location/resolve?q=${encodeURIComponent(value)}`);
  if (!res.ok) {
    document.getElementById("locationLabel").textContent = "位置格式错误，请输入 lat,lng 或预置地点";
    return;
  }
  const data = await res.json();
  state.userLat = data.latitude;
  state.userLng = data.longitude;
  document.getElementById("locationLabel").textContent = `当前位置: ${data.label}`;
  await loadRestaurants();
}

async function locateByBrowser() {
  if (!navigator.geolocation) {
    document.getElementById("locationLabel").textContent = "浏览器不支持定位";
    return;
  }
  navigator.geolocation.getCurrentPosition(
    async (position) => {
      state.userLat = position.coords.latitude;
      state.userLng = position.coords.longitude;
      document.getElementById("locationInput").value = `${state.userLat.toFixed(6)},${state.userLng.toFixed(6)}`;
      document.getElementById("locationLabel").textContent = "定位成功";
      await loadRestaurants();
    },
    () => {
      document.getElementById("locationLabel").textContent = "定位失败，请手动输入";
    }
  );
}

function bindEvents() {
  [...filters, "pet_friendly"].forEach((id) => {
    document.getElementById(id).addEventListener("change", () => {
      state.page = 1;
      loadRestaurants();
    });
  });
  document.getElementById("locateBtn").addEventListener("click", locateByBrowser);
  document.getElementById("applyLocationBtn").addEventListener("click", resolveManualLocation);
}

async function bootstrap() {
  await loadFilterOptions();
  bindEvents();
  await loadRestaurants();
}

bootstrap();
