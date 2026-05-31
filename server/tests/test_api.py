import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

DB_PATH = Path(tempfile.gettempdir()) / "zhoumi_test_api.sqlite"
try:
    DB_PATH.unlink()
except FileNotFoundError:
    pass

os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["ADMIN_TOKEN"] = "test-admin-token"
os.environ["WEATHER_API_KEY"] = ""

from fastapi.testclient import TestClient  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.models import FaqKnowledge, KbPending, PoiIndex, TravelKnowledge, TravelRoute  # noqa: E402
from app.schemas import RecommendPoiOut  # noqa: E402
from app.services import map_provider, weather_provider  # noqa: E402
from app.services.route_builder import build_home_routes  # noqa: E402


class ApiSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_ctx = TestClient(app)
        cls.client = cls.client_ctx.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client_ctx.__exit__(None, None, None)
        try:
            DB_PATH.unlink()
        except FileNotFoundError:
            pass

    def test_catalog_seed_data_is_available(self):
        health = self.client.get("/api/health")
        self.assertEqual(health.status_code, 200)

        capability = self.client.get("/api/capability")
        self.assertEqual(capability.status_code, 200)
        self.assertIn("ai", capability.json())

        geo = self.client.get("/api/geo/city", params={"lat": 30.5728, "lng": 104.0668})
        self.assertEqual(geo.status_code, 200)
        self.assertEqual(geo.json()["city"], "成都")

        pois = self.client.get("/api/poi/list", params={"city": "成都"})
        self.assertEqual(pois.status_code, 200)
        self.assertGreaterEqual(len(pois.json()), 5)

    def test_poi_list_filters_curated_data_by_requested_city(self):
        db = SessionLocal()
        try:
            poi = PoiIndex(
                provider="stub",
                name="上海测试公园",
                city="上海",
                category="公园",
                lat=31.2304,
                lng=121.4737,
                source="test",
            )
            db.add(poi)
            db.flush()
            db.add(TravelKnowledge(
                poi_id=poi.id,
                scene_ids=["family"],
                scene_tags=["亲子"],
                recommend_reason="测试上海 POI",
                play_duration="1h",
                budget_level="免费",
                review_status="approved",
            ))
            db.commit()
        finally:
            db.close()

        response = self.client.get("/api/poi/list", params={"city": "上海"})
        self.assertEqual(response.status_code, 200)
        names = [item["name"] for item in response.json()]
        self.assertIn("上海测试公园", names)
        self.assertNotIn("成都博物馆", names)
        self.assertNotIn("人民公园", names)

    def test_route_recommend_normalizes_requested_city(self):
        db = SessionLocal()
        try:
            db.add(TravelRoute(
                title="成都测试路线",
                city="成都",
                scene="family",
                scene_label="亲子",
                duration="半日",
                budget_level="低",
                poi_ids=[],
                route_text="测试路线",
                review_status="approved",
            ))
            db.commit()
        finally:
            db.close()

        response = self.client.get("/api/route/recommend", params={"city": "成都市"})
        self.assertEqual(response.status_code, 200)
        titles = [item["title"] for item in response.json()]
        self.assertIn("成都测试路线", titles)

    def test_home_feed_requires_user_location(self):
        response = self.client.get("/api/home/feed", params={"city": "成都"})
        self.assertEqual(response.status_code, 422)

    def test_home_feed_uses_reversed_city_before_stale_client_city(self):
        original_reverse = map_provider.amap_reverse_geocode
        try:
            map_provider.amap_reverse_geocode = lambda lat, lng: {"city": "成都", "landmark": None}
            response = self.client.get(
                "/api/home/feed",
                params={"lat": 30.5728, "lng": 104.0668, "city": "广州"},
            )
        finally:
            map_provider.amap_reverse_geocode = original_reverse

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["location"]["city"], "成都")

    def test_home_feed_searches_around_15km(self):
        captured = {}
        original_search = map_provider.amap_search_around

        def fake_search(lat, lng, radius_km=5.0, types=map_provider.AMAP_DEFAULT_TYPES, **_kwargs):
            captured["radius_km"] = radius_km
            return []

        try:
            map_provider.amap_search_around = fake_search
            response = self.client.get(
                "/api/home/feed",
                params={"lat": 30.5728, "lng": 104.0668, "city": "成都"},
            )
        finally:
            map_provider.amap_search_around = original_search

        self.assertEqual(response.status_code, 200)
        self.assertEqual(captured.get("radius_km"), 15.0)

    def test_home_feed_spans_full_radius_with_weight_sort(self):
        # 附近页带半径时应按热度横跨全半径召回，避免只堆积最近一圈
        # （bug：选 15km 列表只拉到 ~4.2km 就没有更多，因 distance 排序只返回最近一批）
        captured = {}
        original_search = map_provider.amap_search_around

        def fake_search(lat, lng, radius_km=5.0, types=map_provider.AMAP_DEFAULT_TYPES,
                        sortrule="distance", pages=1, **_kwargs):
            captured["radius_km"] = radius_km
            captured["sortrule"] = sortrule
            captured["pages"] = pages
            return []

        try:
            map_provider.amap_search_around = fake_search
            response = self.client.get(
                "/api/home/feed",
                params={"lat": 30.5728, "lng": 104.0668, "city": "成都", "radius": 15},
            )
        finally:
            map_provider.amap_search_around = original_search

        self.assertEqual(response.status_code, 200)
        self.assertEqual(captured.get("radius_km"), 15.0)
        self.assertEqual(captured.get("sortrule"), "weight")
        # 大半径需抓多页才能拉到远处，固定 3 页只够最近一圈
        self.assertGreaterEqual(captured.get("pages"), 5)

    def test_weather_uses_amap_live_api_when_key_configured(self):
        calls = []
        original_key = weather_provider.settings.amap_key
        original_httpx = getattr(weather_provider, "httpx", None)

        class FakeResponse:
            def raise_for_status(self):
                return None

            def json(self):
                return {
                    "status": "1",
                    "lives": [{
                        "weather": "小雨",
                        "temperature": "28",
                        "winddirection": "东南",
                        "windpower": "3",
                    }],
                }

        def fake_get(url, params, timeout):
            calls.append((url, params, timeout))
            return FakeResponse()

        try:
            weather_provider.settings.amap_key = "test-amap-key"
            weather_provider.httpx = SimpleNamespace(get=fake_get)
            weather = weather_provider.get_weather("成都")
        finally:
            weather_provider.settings.amap_key = original_key
            if original_httpx is None:
                try:
                    delattr(weather_provider, "httpx")
                except AttributeError:
                    pass
            else:
                weather_provider.httpx = original_httpx

        self.assertEqual(weather.source, "amap")
        self.assertEqual(weather.temp, 28)
        self.assertEqual(weather.cond, "小雨")
        self.assertEqual(weather.icon, "rain")
        self.assertIn("东南风", weather.wind)
        self.assertTrue(calls)

    def test_home_routes_prefer_destinations_inside_15km(self):
        db = SessionLocal()
        try:
            far_poi = PoiIndex(
                provider="stub",
                name="成都远距离路线点",
                city="成都",
                category="景点",
                lat=31.2,
                lng=104.7,
                source="test",
            )
            db.add(far_poi)
            db.flush()
            db.add(TravelRoute(
                title="成都远距离模板路线",
                city="成都",
                scene="family",
                scene_label="亲子",
                duration="一日",
                budget_level="中",
                poi_ids=[far_poi.id],
                route_text="远距离路线不应出现在 15 公里首页推荐里",
                review_status="approved",
            ))
            db.commit()

            recommended = [
                RecommendPoiOut(
                    id=f"near-{i}",
                    name=f"15公里内推荐点{i}",
                    category="景点",
                    distance=f"{i + 1}.0km",
                    reason="附近可去",
                    lat=30.5728 + i * 0.001,
                    lng=104.0668 + i * 0.001,
                    nav_ready=True,
                )
                for i in range(5)
            ]
            routes = build_home_routes(
                db,
                city="成都",
                scene="family",
                origin=(30.5728, 104.0668),
                recommended=recommended,
                limit=3,
            )
        finally:
            db.close()

        self.assertGreaterEqual(len(routes), 1)
        self.assertTrue(str(routes[0].id).startswith("dynamic_"))
        stop_names = [stop.name for route in routes for stop in route.stops]
        self.assertNotIn("成都远距离路线点", stop_names)

    def test_featured_routes_can_return_multiple_routes_for_one_duration(self):
        scene = "route_bucket_test"
        db = SessionLocal()
        try:
            for i in range(9):
                poi = PoiIndex(
                    provider="stub",
                    name=f"成都半日路线候选点{i + 1}",
                    city="成都",
                    category="景点",
                    address=f"成都市路线测试路 {i + 1} 号",
                    lat=30.5728 + i * 0.001,
                    lng=104.0668 + i * 0.001,
                    source="test",
                )
                db.add(poi)
                db.flush()
                db.add(TravelKnowledge(
                    poi_id=poi.id,
                    scene_ids=[scene],
                    scene_tags=["路线"],
                    recommend_reason="用于验证同一时长下有多条线路可选",
                    play_duration="1h",
                    budget_level="低",
                    review_status="approved",
                ))
            db.commit()
        finally:
            db.close()

        response = self.client.get(
            "/api/routes/featured",
            params={
                "lat": 30.5728,
                "lng": 104.0668,
                "city": "成都市",
                "scene": scene,
                "duration": "half",
                "radius": 15,
                "route_per_duration": 3,
            },
        )

        self.assertEqual(response.status_code, 200)
        routes = response.json()
        self.assertEqual(len(routes), 3)
        self.assertTrue(all(route["duration"] == "半日" for route in routes))
        self.assertTrue(all(len(route["stops"]) >= 3 for route in routes))

    def test_dynamic_routes_respect_time_budget_and_allow_many_per_duration(self):
        # 每个时长可出 4 条以上路线；且车程超出该时长的远点不进路线（别光路上就超时）
        origin = (30.5728, 104.0668)
        near = [
            RecommendPoiOut(
                id=f"near-{i}",
                name=f"成都近点{i}",
                category="景点",
                distance=f"0.{i}km",
                reason="附近可去",
                lat=30.5728 + i * 0.001,
                lng=104.0668 + i * 0.001,
                nav_ready=True,
            )
            for i in range(12)
        ]
        far = [
            RecommendPoiOut(
                id=f"far-{i}",
                name=f"成都远点{i}",
                category="景点",
                distance="80km",
                reason="太远",
                lat=31.30 + i * 0.001,   # 距 origin ~80km，往返车程远超 2 小时/一日预算
                lng=104.0668,
                nav_ready=True,
            )
            for i in range(2)
        ]
        db = SessionLocal()
        try:
            routes = build_home_routes(
                db,
                city="路线时间预算测试市",   # 无模板路线，仅验证动态路线
                scene=None,
                origin=origin,
                recommended=near + far,
                limit=60,
                max_per_dur=10,
            )
        finally:
            db.close()

        two_hour = [r for r in routes if r.duration == "2小时"]
        self.assertGreater(len(two_hour), 4)   # 不再卡在 4 条
        stop_names = {stop.name for route in routes for stop in route.stops}
        self.assertNotIn("成都远点0", stop_names)
        self.assertNotIn("成都远点1", stop_names)

    def test_plan_aligned_api_aliases_are_available(self):
        db = SessionLocal()
        try:
            poi = PoiIndex(
                provider="stub",
                name="成都方案接口测试公园",
                city="成都",
                category="公园",
                address="成都市接口路 1 号",
                lat=30.5731,
                lng=104.0671,
                source="test",
            )
            db.add(poi)
            db.flush()
            db.add(TravelKnowledge(
                poi_id=poi.id,
                scene_ids=["family"],
                scene_tags=["亲子", "免费"],
                recommend_reason="用于验证方案命名接口的附近推荐",
                play_duration="1h",
                budget_level="免费",
                review_status="approved",
            ))
            db.add(TravelRoute(
                title="成都方案接口 2 小时路线",
                city="成都",
                scene="family",
                scene_label="亲子",
                duration="2小时",
                budget_level="低",
                poi_ids=[poi.id],
                route_text="方案接口路线",
                review_status="approved",
            ))
            db.commit()
        finally:
            db.close()

        params = {"lat": 30.5728, "lng": 104.0668, "city": "成都市", "scene": "family"}

        bootstrap = self.client.get("/api/home/bootstrap", params=params)
        self.assertEqual(bootstrap.status_code, 200)
        self.assertIn("nearby_now", bootstrap.json())

        nearby = self.client.get("/api/nearby/recommend", params=params)
        self.assertEqual(nearby.status_code, 200)
        self.assertTrue(any(item["name"] == "成都方案接口测试公园" for item in nearby.json()))
        self.assertTrue(all(item["nav_ready"] for item in nearby.json()))

        routes = self.client.get("/api/routes/featured", params=params)
        self.assertEqual(routes.status_code, 200)
        self.assertTrue(any(route["stops"] for route in routes.json()))

        consult = self.client.post(
            "/api/consult/ask",
            json={
                "question": "带孩子 2 小时内去哪？",
                "city": "成都市",
                "lat": 30.5728,
                "lng": 104.0668,
                "scene": "family",
            },
        )
        self.assertEqual(consult.status_code, 200)
        answer = consult.json()
        self.assertIn("sources", answer)
        self.assertIn("destinations", answer)
        self.assertIn("routes", answer)

    def test_home_feed_returns_navigable_recommendations(self):
        db = SessionLocal()
        try:
            nav_poi = PoiIndex(
                provider="stub",
                name="成都可导航亲子公园",
                city="成都",
                category="公园",
                address="成都市测试路 1 号",
                lat=30.5730,
                lng=104.0670,
                source="test",
            )
            missing_coord_poi = PoiIndex(
                provider="stub",
                name="成都缺坐标室内馆",
                city="成都",
                category="室内馆",
                address="成都市测试路 2 号",
                source="test",
            )
            db.add(nav_poi)
            db.add(missing_coord_poi)
            db.flush()
            db.add(TravelKnowledge(
                poi_id=nav_poi.id,
                scene_ids=["family", "budget"],
                scene_tags=["亲子", "免费"],
                recommend_reason="距离近，适合带孩子短时散步",
                play_duration="1h",
                budget_level="免费",
                best_time="下午",
                review_status="approved",
            ))
            db.add(TravelKnowledge(
                poi_id=missing_coord_poi.id,
                scene_ids=["family"],
                scene_tags=["亲子"],
                recommend_reason="这条没有坐标，不能进入导航推荐",
                play_duration="1h",
                budget_level="免费",
                review_status="approved",
            ))
            db.add(TravelRoute(
                title="成都亲子短线",
                city="成都",
                scene="family",
                scene_label="亲子",
                duration="2小时",
                budget_level="低",
                poi_ids=[nav_poi.id],
                route_text="近距离低强度亲子路线",
                review_status="approved",
            ))
            db.commit()
        finally:
            db.close()

        response = self.client.get(
            "/api/home/feed",
            params={
                "lat": 30.5728,
                "lng": 104.0668,
                "city": "成都市",
                "intent": "nearby_now",
                "scene": "family",
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["location"]["city"], "成都")
        self.assertEqual(
            [entry["id"] for entry in data["entries"]],
            ["place_index", "nearby_now", "hot_routes", "assistant"],
        )
        self.assertIn("weather", data)
        self.assertGreaterEqual(len(data["scene_index"]), 1)
        self.assertGreaterEqual(len(data["assistant_chips"]), 1)

        names = [item["name"] for item in data["nearby_now"]]
        self.assertIn("成都可导航亲子公园", names)
        self.assertNotIn("成都缺坐标室内馆", names)

        target = next(item for item in data["nearby_now"] if item["name"] == "成都可导航亲子公园")
        self.assertEqual(target["category"], "公园")
        self.assertEqual(target["kb_status"], "hit")
        self.assertTrue(target["nav_ready"])
        self.assertIsInstance(target["score"], int)
        self.assertTrue(target["reason"])
        self.assertIn("亲子", target["tags"])
        self.assertIsNotNone(target["lat"])
        self.assertIsNotNone(target["lng"])

        self.assertGreaterEqual(len(data["routes"]), 1)
        self.assertTrue(any(route["nav_ready"] for route in data["routes"]))
        route_stop_names = [
            stop["name"]
            for route in data["routes"]
            for stop in route["stops"]
        ]
        self.assertIn("成都可导航亲子公园", route_stop_names)

    def test_poi_detail_returns_existing_poi_coordinates(self):
        db = SessionLocal()
        try:
            poi = PoiIndex(
                provider="amap",
                provider_poi_id="detail-test-poi",
                name="成都详情接口测试点",
                city="成都",
                category="景点",
                address="成都市详情测试路 1 号",
                lat=30.5730,
                lng=104.0670,
                source="test",
            )
            db.add(poi)
            db.commit()
            poi_id = poi.id
        finally:
            db.close()

        response = self.client.get(
            "/api/poi/detail",
            params={"id": poi_id, "lat": 30.5728, "lng": 104.0668},
        )

        self.assertEqual(response.status_code, 200)
        detail = response.json()
        self.assertEqual(detail["id"], poi_id)
        self.assertEqual(detail["name"], "成都详情接口测试点")
        self.assertEqual(detail["lat"], 30.5730)
        self.assertEqual(detail["lng"], 104.0670)

    def test_generate_plan_does_not_claim_realtime_weather_without_provider(self):
        response = self.client.post(
            "/api/trip/generate",
            json={
                "city": "成都",
                "time": "周六清晨",
                "people_type": "2人",
                "budget": "200元以内",
                "transport": "自驾",
                "preferences": ["钓鱼"],
                "scene": "fish",
            },
        )
        self.assertEqual(response.status_code, 200)
        plan = response.json()
        self.assertTrue(plan["disclaimer"])
        self.assertGreaterEqual(len(plan["stops"]), 1)

        fetched = self.client.get("/api/trip/plan", params={"no": plan["no"]})
        self.assertEqual(fetched.status_code, 200)
        self.assertEqual(fetched.json()["no"], plan["no"])

        weather_sources = [s["t"] for s in plan["sources"] if s["kind"] == "天气"]
        self.assertTrue(weather_sources)
        self.assertNotIn("实时气象 API", weather_sources)

    def test_generate_plan_stays_inside_requested_city(self):
        response = self.client.post(
            "/api/trip/generate",
            json={
                "city": "上海",
                "time": "今天",
                "people_type": "朋友",
                "budget": "100元以内",
                "transport": "公交",
                "preferences": ["钓鱼"],
                "scene": "fish",
            },
        )
        self.assertEqual(response.status_code, 200)
        plan = response.json()
        self.assertEqual(plan["title"], "上海出游方案")
        self.assertEqual(plan["stops"], [])

    def test_generate_plan_normalizes_requested_city(self):
        db = SessionLocal()
        try:
            poi = PoiIndex(
                provider="stub",
                name="成都归一化测试点",
                city="成都",
                category="公园",
                lat=30.5728,
                lng=104.0668,
                source="test",
            )
            db.add(poi)
            db.flush()
            db.add(TravelKnowledge(
                poi_id=poi.id,
                scene_ids=["test_family"],
                scene_tags=["亲子"],
                recommend_reason="测试城市归一化",
                play_duration="1h",
                budget_level="免费",
                review_status="approved",
            ))
            db.add(TravelRoute(
                title="成都归一化路线",
                city="成都",
                scene="test_family",
                scene_label="测试亲子",
                duration="半日",
                budget_level="低",
                poi_ids=[poi.id],
                route_text="测试路线",
                review_status="approved",
            ))
            db.commit()
        finally:
            db.close()

        response = self.client.post(
            "/api/trip/generate",
            json={
                "city": "成都市",
                "time": "今天",
                "people_type": "亲子",
                "budget": "100元以内",
                "transport": "公交",
                "preferences": ["带娃友好"],
                "scene": "test_family",
            },
        )
        self.assertEqual(response.status_code, 200)
        plan = response.json()
        self.assertEqual(plan["title"], "成都归一化路线")
        self.assertEqual(plan["stops"][0]["name"], "成都归一化测试点")

    def test_known_question_hits_kb(self):
        response = self.client.post(
            "/api/kb/ask",
            json={"question": "钓点限钓吗？", "city": "成都"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["from_kb"])
        self.assertEqual(data["sources"][0]["k"], "知识库")

    def test_location_aware_assistant_handles_kilometer_distances(self):
        response = self.client.post(
            "/api/kb/ask",
            json={
                "question": "带孩子 2 小时内去哪？",
                "city": "成都",
                "lat": 30.5728,
                "lng": 104.0668,
                "scene": "family",
                "intent": "assistant",
                "history": [],
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("destinations", data)
        self.assertGreaterEqual(len(data["destinations"]), 1)
        self.assertRegex(data["destinations"][0]["distance"], r"(m|km)$")

    def test_kb_answer_stays_inside_requested_city(self):
        response = self.client.post(
            "/api/kb/ask",
            json={"question": "下雨改去哪？", "city": "上海"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["from_kb"])
        self.assertNotIn("乌鲁木齐", data["text"])
        self.assertNotIn("大巴扎", data["text"])

    def test_ask_stream_returns_ndjson_events(self):
        with self.client.stream(
            "POST",
            "/api/kb/ask_stream",
            json={"question": "钓点限钓吗？", "city": "成都"},
        ) as response:
            self.assertEqual(response.status_code, 200)
            body = "".join(response.iter_text())

        self.assertIn('"event":"meta"', body)
        self.assertIn('"event":"text"', body)
        self.assertIn('"event":"done"', body)
        self.assertIn("垂钓", body)

    def test_admin_endpoint_requires_token(self):
        response = self.client.get("/api/admin/kb/pending")
        self.assertEqual(response.status_code, 401)

    def test_feedback_creates_pending_review_record(self):
        comment = "路线里第二站停车信息不清楚，请补充停车入口"
        response = self.client.post(
            "/api/feedback",
            json={
                "target_type": "plan",
                "target_id": "PLAN-TEST",
                "useful": False,
                "comment": comment,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json()["id"])

        feedback_list = self.client.get("/api/feedback/list")
        self.assertEqual(feedback_list.status_code, 200)
        self.assertIn(comment, "\n".join(item["content"] for item in feedback_list.json()))

        pending = self.client.get(
            "/api/admin/kb/pending",
            headers={"X-Admin-Token": "test-admin-token"},
        )
        self.assertEqual(pending.status_code, 200)
        pending_text = "\n".join(
            f"{item.get('question')}\n{item.get('generated_answer')}"
            for item in pending.json()
        )
        self.assertIn(comment, pending_text)

    def test_admin_ai_analyze_reviews_pending_knowledge(self):
        db = SessionLocal()
        try:
            pending = KbPending(
                question="成都博物馆门票多少钱？",
                generated_answer="成都博物馆免费开放，开放时间请以官方和地图实时查询为准。",
                source_urls=["https://example.com/museum"],
                city="成都",
                category="门票",
                risk_level="低",
                status="pending",
            )
            db.add(pending)
            db.commit()
            pending_id = pending.id
        finally:
            db.close()

        analyzed = self.client.post(
            "/api/admin/kb/analyze",
            headers={"X-Admin-Token": "test-admin-token"},
            json={"id": pending_id},
        )
        self.assertEqual(analyzed.status_code, 200)
        analysis = analyzed.json()
        self.assertEqual(analysis["id"], pending_id)
        self.assertIn(analysis["suggested_status"], ["approved", "needs_update", "rejected"])
        self.assertGreaterEqual(len(analysis["issues"]), 1)
        self.assertTrue(analysis["revised_answer"])

        approved = self.client.post(
            "/api/admin/kb/approve",
            headers={"X-Admin-Token": "test-admin-token"},
            json={
                "id": pending_id,
                "status": analysis["suggested_status"],
                "generated_answer": analysis["revised_answer"],
            },
        )
        self.assertEqual(approved.status_code, 200)

        db = SessionLocal()
        try:
            saved = (
                db.query(FaqKnowledge)
                .filter(FaqKnowledge.question == "成都博物馆门票多少钱？")
                .order_by(FaqKnowledge.id.desc())
                .first()
            )
            if analysis["suggested_status"] == "approved":
                self.assertIsNotNone(saved)
                self.assertEqual(saved.answer, analysis["revised_answer"])
            else:
                self.assertIsNone(saved)
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
