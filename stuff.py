def est_prime(n):
    """Renvoie True si n est un nombre premier, False sinon."""
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def recevoir_nombres_primes(n):
    """Renvoie une liste de tous les nombres premiers jusqu'à n."""
    primes = []
    for prime_possible in range(2, n + 1):
        if est_prime(prime_possible):
            primes.append(prime_possible)
    return primes

def main():
    continuee = True
    while continuee == True:
        entree = input("Entrez un nombre pour trouver tous les nombres premiers jusqu'à ce nombre (ou « q » pour quitter) :").lower()
        if entree == 'q':
            break
        try:
            nombre = int(entree)
            if nombre < 1:
                raise ValueError("Le nombre doit être supérieur à 0.")
        except ValueError as e:
            print(f"Entrée invalide: {e}")
            continue
        primes = recevoir_nombres_primes(nombre)
        print(f"Nombres premiers jusqu'à {nombre}:")
        print("\n".join(map(str, primes)))
        continuee = bool(input("Voulez vous continuer? (y/n): "))
        if continuee == "y":
            continue
        else:
            break


if __name__ == "__main__":
    main()