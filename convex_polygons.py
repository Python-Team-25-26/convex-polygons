from math import sqrt

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
            Выпуклость определяется по определению:

            Все углы лежат по одну сторону прямой, проходящей через два угла, и так для каждой пары углов.

            Сжатая ссылка на stack overflow - https://shorturl.at/ERZBS
        """
         
        if len(self._vertices) < 3:
            return False
            
        n = len(self._vertices)
        sign = 0
        
        
        for i in range(n):
        
            # Берем три последовательные вершины
            x1, y1 = self._vertices[i]
            x2, y2 = self._vertices[(i + 1) % n]
            x3, y3 = self._vertices[(i + 2) % n]
            
            # Вычисляем векторное произведение векторов (v2-v1) и (v3-v2)
            # Это показывает, в какую сторону поворачивает многоугольник
            cross_product = (x2 - x1) * (y3 - y2) - (y2 - y1) * (x3 - x2)
            
            if cross_product == 0:
                continue
                
            if sign == 0:
                sign = 1 if cross_product > 0 else -1
            else:
                # Если знак отличается от предыдущих - многоугольник невыпуклый
                current_sign = 1 if cross_product > 0 else -1
                if current_sign != sign:
                    return False
                    
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
            total += sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return total
    
    def contains(self, point):
        """
        Для выпуклого многоугольника точка внутри, если она находится по одну сторону от всех ребер
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
        pass
    
    def triangulate(self):
        pass
    
    def __str__(self):
        return f"ConvexPolygon({self._vertices})"
    

if __name__ == "__main__":

    square = ConvexPolygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    print(f"Квадрат: {square}")
    print(f"Площадь квадрата: {square.area}")
    print(f"Периметр квадрата: {square.perimeter}")

    triangle = ConvexPolygon([(0, 0), (2, 0), (1, 2)])
    print(f"\nТреугольник: {triangle}")
    print(f"Площадь треугольника: {triangle.area}")
    print(f"Периметр треугольника: {triangle.perimeter}")

    test_points = [(0.5, 0.5), (1.5, 0.5), (2.5, 2.5)]
    for point in test_points:
        in_square = square.contains(point)
        in_triangle = triangle.contains(point)
        print(f"Точка {point}: в квадрате - {in_square}, в треугольнике - {in_triangle}")