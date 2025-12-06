#!/usr/bin/env python3
"""
Digital Utopia Platform - Comprehensive Project Evaluation Script
Đánh giá toàn diện dự án Digital Utopia Platform
"""

import os
import json
from pathlib import Path
from datetime import datetime
import re

class ProjectEvaluator:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "backend": {},
            "frontend": {},
            "database": {},
            "tests": {},
            "documentation": {},
            "overall": {}
        }
    
    def evaluate_backend(self):
        """Đánh giá backend - FastAPI endpoints, models, services"""
        backend_path = self.base_path / "backend"
        
        # Count API endpoints
        api_endpoints = []
        total_endpoints = 0
        api_dir = backend_path / "app" / "api" / "endpoints"
        
        if api_dir.exists():
            for file in api_dir.glob("*.py"):
                if file.name != "__init__.py":
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Count route decorators
                        get_count = len(re.findall(r'@router\.(get|post|put|delete|patch)', content))
                        app_count = len(re.findall(r'@app\.(get|post|put|delete|patch)', content))
                        endpoints = get_count + app_count
                        total_endpoints += endpoints
                        
                        api_endpoints.append({
                            "module": file.stem,
                            "file": file.name,
                            "endpoints": endpoints
                        })
        
        # Count models
        models = []
        models_dir = backend_path / "app" / "models"
        if models_dir.exists():
            for file in models_dir.glob("*.py"):
                if file.name not in ["__init__.py", "base.py"]:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Count class definitions
                        classes = len(re.findall(r'class \w+\(.*\):', content))
                        models.append({
                            "module": file.stem,
                            "file": file.name,
                            "classes": classes
                        })
        
        # Count services
        services = []
        services_dir = backend_path / "app" / "services"
        if services_dir.exists():
            for file in services_dir.glob("*.py"):
                if file.name != "__init__.py":
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Count functions and class methods
                        functions = len(re.findall(r'def \w+\(', content))
                        services.append({
                            "module": file.stem,
                            "file": file.name,
                            "functions": functions
                        })
        
        self.results["backend"] = {
            "api_endpoints": api_endpoints,
            "total_endpoints": total_endpoints,
            "models": models,
            "total_models": len(models),
            "services": services,
            "total_services": len(services),
            "completion_rate": self._calculate_backend_completion(total_endpoints, len(models), len(services))
        }
    
    def evaluate_frontend(self):
        """Đánh giá frontend - Client App và Admin App"""
        
        # Evaluate Client App
        client_app_path = self.base_path / "client-app"
        client_components = []
        client_views = []
        
        if client_app_path.exists():
            # Count components
            components_dir = client_app_path / "src" / "components"
            if components_dir.exists():
                for file in components_dir.rglob("*.vue"):
                    client_components.append(str(file.relative_to(client_app_path)))
            
            # Count views/pages
            views_dir = client_app_path / "src" / "views"
            if views_dir.exists():
                for file in views_dir.rglob("*.vue"):
                    client_views.append(str(file.relative_to(client_app_path)))
        
        # Evaluate Admin App
        admin_app_path = self.base_path / "Admin-app"
        admin_components = []
        admin_views = []
        
        if admin_app_path.exists():
            # Count components
            components_dir = admin_app_path / "src" / "components"
            if components_dir.exists():
                for file in components_dir.rglob("*.vue"):
                    admin_components.append(str(file.relative_to(admin_app_path)))
            
            # Count views/pages
            views_dir = admin_app_path / "src" / "views"
            if views_dir.exists():
                for file in views_dir.rglob("*.vue"):
                    admin_views.append(str(file.relative_to(admin_app_path)))
        
        self.results["frontend"] = {
            "client_app": {
                "components": len(client_components),
                "views": len(client_views),
                "total_files": len(client_components) + len(client_views)
            },
            "admin_app": {
                "components": len(admin_components),
                "views": len(admin_views),
                "total_files": len(admin_components) + len(admin_views)
            },
            "completion_rate": self._calculate_frontend_completion(
                len(client_components) + len(client_views),
                len(admin_components) + len(admin_views)
            )
        }
    
    def evaluate_database(self):
        """Đánh giá database schema và migrations"""
        backend_path = self.base_path / "backend"
        
        # Check for Alembic migrations
        migrations = []
        alembic_dir = backend_path / "alembic" / "versions"
        if alembic_dir.exists():
            for file in alembic_dir.glob("*.py"):
                migrations.append(file.name)
        
        # Count database models (from models directory)
        total_models = self.results.get("backend", {}).get("total_models", 0)
        
        self.results["database"] = {
            "migrations": len(migrations),
            "models": total_models,
            "has_alembic": (backend_path / "alembic.ini").exists(),
            "completion_rate": self._calculate_database_completion(len(migrations), total_models)
        }
    
    def evaluate_tests(self):
        """Đánh giá test coverage và test files"""
        backend_path = self.base_path / "backend"
        
        test_files = []
        
        # Backend tests
        for test_file in backend_path.glob("test*.py"):
            test_files.append(str(test_file.relative_to(self.base_path)))
        
        tests_dir = backend_path / "tests"
        if tests_dir.exists():
            for test_file in tests_dir.rglob("test*.py"):
                test_files.append(str(test_file.relative_to(self.base_path)))
        
        # Count test functions
        total_test_functions = 0
        for test_file_path in test_files:
            full_path = self.base_path / test_file_path
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    total_test_functions += len(re.findall(r'def test_\w+\(', content))
        
        self.results["tests"] = {
            "test_files": test_files,
            "total_test_files": len(test_files),
            "total_test_functions": total_test_functions,
            "completion_rate": self._calculate_test_completion(len(test_files), total_test_functions)
        }
    
    def evaluate_documentation(self):
        """Đánh giá documentation"""
        doc_files = []
        
        for md_file in self.base_path.glob("*.md"):
            size = md_file.stat().st_size
            doc_files.append({
                "file": md_file.name,
                "size_kb": round(size / 1024, 2)
            })
        
        # Count Vietnamese documentation
        vietnamese_docs = [doc for doc in doc_files if any(
            vn_indicator in doc["file"].lower() 
            for vn_indicator in ["giao-dien", "tieng-viet", "vietnamese"]
        )]
        
        self.results["documentation"] = {
            "total_files": len(doc_files),
            "doc_files": doc_files,
            "vietnamese_docs": len(vietnamese_docs),
            "completion_rate": self._calculate_documentation_completion(len(doc_files))
        }
    
    def _calculate_backend_completion(self, endpoints, models, services):
        """Tính tỷ lệ hoàn thành backend dựa trên mục tiêu"""
        # Expected: 72 endpoints, 8+ models, 8+ services (theo README)
        endpoint_score = min(endpoints / 72 * 100, 100)
        model_score = min(models / 8 * 100, 100)
        service_score = min(services / 8 * 100, 100)
        
        return round((endpoint_score + model_score + service_score) / 3, 2)
    
    def _calculate_frontend_completion(self, client_files, admin_files):
        """Tính tỷ lệ hoàn thành frontend"""
        # Expected: ~80 client files, ~40 admin files (based on current structure)
        client_score = min(client_files / 80 * 100, 100)
        admin_score = min(admin_files / 40 * 100, 100)
        
        return round((client_score + admin_score) / 2, 2)
    
    def _calculate_database_completion(self, migrations, models):
        """Tính tỷ lệ hoàn thành database"""
        # Expected: có migrations và models đầy đủ
        migration_score = min(migrations / 5 * 100, 100) if migrations > 0 else 0
        model_score = min(models / 8 * 100, 100)
        
        return round((migration_score + model_score) / 2, 2)
    
    def _calculate_test_completion(self, test_files, test_functions):
        """Tính tỷ lệ hoàn thành tests"""
        # Expected: 5+ test files, 50+ test functions
        file_score = min(test_files / 5 * 100, 100)
        function_score = min(test_functions / 50 * 100, 100)
        
        return round((file_score + function_score) / 2, 2)
    
    def _calculate_documentation_completion(self, doc_files):
        """Tính tỷ lệ hoàn thành documentation"""
        # Expected: 10+ documentation files
        return round(min(doc_files / 10 * 100, 100), 2)
    
    def calculate_overall_completion(self):
        """Tính tỷ lệ hoàn thiện tổng thể của dự án"""
        backend_rate = self.results["backend"].get("completion_rate", 0)
        frontend_rate = self.results["frontend"].get("completion_rate", 0)
        database_rate = self.results["database"].get("completion_rate", 0)
        test_rate = self.results["tests"].get("completion_rate", 0)
        doc_rate = self.results["documentation"].get("completion_rate", 0)
        
        # Weighted average: Backend (30%), Frontend (30%), Database (15%), Tests (15%), Docs (10%)
        overall = (
            backend_rate * 0.30 +
            frontend_rate * 0.30 +
            database_rate * 0.15 +
            test_rate * 0.15 +
            doc_rate * 0.10
        )
        
        self.results["overall"] = {
            "completion_rate": round(overall, 2),
            "backend_weight": "30%",
            "frontend_weight": "30%",
            "database_weight": "15%",
            "tests_weight": "15%",
            "documentation_weight": "10%",
            "status": self._get_status(overall)
        }
        
        return overall
    
    def _get_status(self, completion_rate):
        """Xác định trạng thái dựa trên tỷ lệ hoàn thành"""
        if completion_rate >= 95:
            return "Hoàn thiện xuất sắc"
        elif completion_rate >= 80:
            return "Hoàn thiện tốt"
        elif completion_rate >= 60:
            return "Đang phát triển"
        elif completion_rate >= 40:
            return "Đang trong giai đoạn đầu"
        else:
            return "Mới bắt đầu"
    
    def run_full_evaluation(self):
        """Chạy đánh giá toàn diện"""
        print("🔍 Bắt đầu đánh giá dự án Digital Utopia Platform...")
        
        print("   ├─ Đánh giá Backend...")
        self.evaluate_backend()
        
        print("   ├─ Đánh giá Frontend...")
        self.evaluate_frontend()
        
        print("   ├─ Đánh giá Database...")
        self.evaluate_database()
        
        print("   ├─ Đánh giá Tests...")
        self.evaluate_tests()
        
        print("   ├─ Đánh giá Documentation...")
        self.evaluate_documentation()
        
        print("   └─ Tính toán tỷ lệ hoàn thành tổng thể...")
        self.calculate_overall_completion()
        
        print("✅ Đánh giá hoàn tất!\n")
        
        return self.results
    
    def save_results(self, output_file="evaluation_results.json"):
        """Lưu kết quả đánh giá ra file JSON"""
        output_path = self.base_path / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"📁 Kết quả đã được lưu vào: {output_path}")
    
    def print_summary(self):
        """In tóm tắt kết quả đánh giá"""
        print("\n" + "="*80)
        print("📊 TÓM TẮT KẾT QUẢ ĐÁNH GIÁ DỰ ÁN")
        print("="*80)
        
        # Backend
        backend = self.results["backend"]
        print(f"\n🔧 BACKEND:")
        print(f"   • API Endpoints: {backend['total_endpoints']}/72 ({backend['completion_rate']}%)")
        print(f"   • Models: {backend['total_models']}")
        print(f"   • Services: {backend['total_services']}")
        
        # Frontend
        frontend = self.results["frontend"]
        print(f"\n🎨 FRONTEND:")
        print(f"   • Client App: {frontend['client_app']['total_files']} files")
        print(f"   • Admin App: {frontend['admin_app']['total_files']} files")
        print(f"   • Tỷ lệ hoàn thành: {frontend['completion_rate']}%")
        
        # Database
        database = self.results["database"]
        print(f"\n🗄️  DATABASE:")
        print(f"   • Migrations: {database['migrations']}")
        print(f"   • Models: {database['models']}")
        print(f"   • Tỷ lệ hoàn thành: {database['completion_rate']}%")
        
        # Tests
        tests = self.results["tests"]
        print(f"\n🧪 TESTS:")
        print(f"   • Test Files: {tests['total_test_files']}")
        print(f"   • Test Functions: {tests['total_test_functions']}")
        print(f"   • Tỷ lệ hoàn thành: {tests['completion_rate']}%")
        
        # Documentation
        docs = self.results["documentation"]
        print(f"\n📚 DOCUMENTATION:")
        print(f"   • Total Files: {docs['total_files']}")
        print(f"   • Vietnamese Docs: {docs['vietnamese_docs']}")
        print(f"   • Tỷ lệ hoàn thành: {docs['completion_rate']}%")
        
        # Overall
        overall = self.results["overall"]
        print(f"\n" + "="*80)
        print(f"🎯 TỶ LỆ HOÀN THIỆN TỔNG THỂ: {overall['completion_rate']}%")
        print(f"📈 TRẠNG THÁI: {overall['status']}")
        print("="*80 + "\n")


if __name__ == "__main__":
    evaluator = ProjectEvaluator()
    results = evaluator.run_full_evaluation()
    evaluator.print_summary()
    evaluator.save_results()
