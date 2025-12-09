import math
from math import sqrt

EPS = 1e-9
def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1])

def _cross(a, b):
    return a[0]*b[1] - a[1]*b[0]

class ConvexPolygon:
    """
    Класс выпуклых многоугольников на плоскости.

    Многоугольник создается из списка вершин в порядке обхода против часовой стрелки.
    Каждая вершина хранится в виде tuple (x, y).
    """

    def __init__(self, vertices):
        self._vertices = vertices
        if not self._is_convex():
            raise ValueError("Polygon is not convex")

    def _is_convex(self):
        """
        Проверяет, является ли многоугольник выпуклым.
        Все углы должны лежать по одну сторону от прямой, проходящей через два угла.
        """
        
        if len(self._vertices) < 3:
            return False

        n = len(self._vertices)
        sign = None 

        for i in range(n):
            # Берем три последовательные вершины
            x1, y1 = self._vertices[i]
            x2, y2 = self._vertices[(i + 1) % n]
            x3, y3 = self._vertices[(i + 2) % n]

            # Вычисляем векторное произведение
            cross_product = (x2 - x1) * (y3 - y2) - (y2 - y1) * (x3 - x2)

            if cross_product == 0:
                continue

            # Определяем направление поворота
            current_positive = cross_product > 0

            if sign is None:
                # Первое ненулевое значение устанавливает знак
                sign = current_positive
            else:
                # Если направление поворота изменилось - многоугольник невыпуклый
                if current_positive != sign:
                    return False

        # Если все ненулевые кросс-продукты одного знака (или все нулевые) - многоугольник выпуклый
        return True

    @property
    def area(self):
        """
        Используется формула Гаусса

        Сжатая ссылка на Wiki: https://shorturl.at/cv16x
        """
        total = 0
        n = len(self._vertices)
        for i in range(n):
            x1, y1 = self._vertices[i]
            x2, y2 = self._vertices[(i + 1) % n]
            total += (x1 * y2 - x2 * y1)
        return abs(total) / 2

    @property
    def perimeter(self):
        total = 0
        n = len(self._vertices)
        for i in range(n):
            x1, y1 = self._vertices[i]
            x2, y2 = self._vertices[(i + 1) % n]
            total += sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return total

    def contains(self, point):
        """
        Для выпуклого многоугольника точка внутри, если она находится по одну сторону от всех рёбер.
        """
        px, py = point
        n = len(self._vertices)
        for i in range(n):
            x1, y1 = self._vertices[i]
            x2, y2 = self._vertices[(i + 1) % n]
            cross_product = (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)
            if cross_product < 0:
                return False
        return True

    def intersection(self, other):
        """
        Sutherland–Hodgman: обрезаем self по всем рёбрам other
        """
        def seg_line_intersection(p1, p2, q1, q2):
            """Пересечение сегмента p1-p2 с прямой q1-q2"""
            r = _sub(p2, p1)
            s = _sub(q2, q1)
            denom = _cross(r, s)
            if abs(denom) < EPS:
                return None
            qp = _sub(q1, p1)
            t = _cross(qp, s) / denom
            if t < -EPS or t > 1 + EPS:
                return None
            return (p1[0] + t * r[0], p1[1] + t * r[1])

        def is_inside(pt, a, b):
            """Для CCW-отсекателя: внутри - это слева от ребра ab"""
            return _cross(_sub(b, a), _sub(pt, a)) >= -EPS

        output = list(self._vertices)
        if not output or not other._vertices:
            return False, [], 0.0

        for i in range(len(other._vertices)):
            a = other._vertices[i]
            b = other._vertices[(i + 1) % len(other._vertices)]
            input_list = output
            output = []
            if not input_list:
                break
            prev = input_list[-1]
            prev_in = is_inside(prev, a, b)
            for curr in input_list:
                curr_in = is_inside(curr, a, b)
                if prev_in and curr_in:
                    # в -> в : добавляем текущую
                    output.append(curr)
                elif prev_in and not curr_in:
                    # в -> вне : добавляем точку пересечения
                    ip = seg_line_intersection(prev, curr, a, b)
                    if ip is not None:
                        output.append(ip)
                elif (not prev_in) and curr_in:
                    # вне -> в : добавляем пересечение и  текущую вершину
                    ip = seg_line_intersection(prev, curr, a, b)
                    if ip is not None:
                        output.append(ip)
                    output.append(curr)
                # вне->вне — ничего не добавляем
                prev = curr
                prev_in = curr_in

        # удалить близкие дубликаты точек (шум от пересечений)
        def remove_close(points, eps=1e-8):
            if not points:
                return []
            res = [points[0]]
            for p in points[1:]:
                if math.hypot(p[0]-res[-1][0], p[1]-res[-1][1]) > eps:
                    res.append(p)
            if len(res) > 1 and math.hypot(res[0][0]-res[-1][0], res[0][1]-res[-1][1]) <= eps:
                res.pop()
            return res

        output = remove_close(output)

        if len(output) < 3:
            return False, [], 0.0

        # вычисляем ориентированную площадь чтобы убедиться в порядке вершин
        signed = 0.0
        n = len(output)
        for i in range(n):
            x1, y1 = output[i]
            x2, y2 = output[(i + 1) % n]
            signed += x1 * y2 - x2 * y1

        if signed < -EPS:
            output.reverse()
            signed = -signed

        area = abs(signed) / 2.0
        return True, output, area


    def triangulate(self):
        """
        Разбивает выпуклый многоугольник на треугольники.
        Возвращает список треугольников (каждый — список из трёх вершин).
        Для выпуклого многоугольника просто соединяем первую вершину с остальными.
        """
        triangles = []
        if len(self._vertices) < 3:
            return []
        for i in range(1, len(self._vertices) - 1):
            triangle = [self._vertices[0], self._vertices[i], self._vertices[i + 1]]
            triangles.append(triangle)
        return triangles


    def __str__(self):
        return f"ConvexPolygon({self._vertices})"


if __name__ == "__main__":
    square = ConvexPolygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    triangle = ConvexPolygon([(0, 0), (2, 0), (1, 2)])
    print(f"Квадрат: {square}")
    print(f"Площадь квадрата: {square.area}")
    print(f"Периметр квадрата: {square.perimeter}")

    print(f"\nТреугольник: {triangle}")
    print(f"Площадь треугольника: {triangle.area}")
    print(f"Периметр треугольника: {triangle.perimeter}")

    test_points = [(0.5, 0.5), (1.5, 0.5), (2.5, 2.5)]
    for point in test_points:
        in_square = square.contains(point)
        in_triangle = triangle.contains(point)
        print(f"Точка {point}: в квадрате - {in_square}, в треугольнике - {in_triangle}")

    has_intersection, intersection_poly, intersection_area = square.intersection(triangle)
    print(f"\n1 Пересечение существует: {has_intersection}")
    if has_intersection:
        print(f"1 Вершины полигона пересечения: {intersection_poly}")
        print(f"1 Площадь пересечения: {intersection_area:.2f}")
    else:
        print("1 Многоугольники не пересекаются")

    square1 = ConvexPolygon([(0, 0), (2, 0), (2, 2), (0, 2)])
    square2 = ConvexPolygon([(1, 1), (3, 1), (3, 3), (1, 3)])
    has_intersection2, intersection_poly2, intersection_area2 = square1.intersection(square2)
    print(f"\n2 Пересечение существует: {has_intersection2}")
    if has_intersection2:
        print(f"2 Вершины полигона пересечения: {intersection_poly2}")
        print(f"2 Площадь пересечения: {intersection_area2:.2f}")
    else:
        print("2 Многоугольники не пересекаются")

    print("\nТриангуляция квадрата:")
    for tri in square1.triangulate():
        print(tri)

    print("\nТриангуляция треугольника:")
    for tri in triangle.triangulate():
        print(tri)

    polygon = ConvexPolygon([(0, 0), (3, 0), (2, 2), (1, 3), (0, 2)])
    print("\nТриангуляция полигона:")
    for tri in polygon.triangulate():
        print(tri)

    has_intersection3, intersection_poly3, intersection_area3 = polygon.intersection(triangle)
    print(f"\n3 Пересечение существует: {has_intersection2}")
    if has_intersection2:
        print(f"3 Вершины полигона пересечения: {intersection_poly2}")
        print(f"3 Площадь пересечения: {intersection_area2:.2f}")
    else:
        print("3 Многоугольники не пересекаются")