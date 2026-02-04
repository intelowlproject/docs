# Upgrade from GreedyBear 1.x
For the upgrade from GreedyBear 1.x manual intervention is required, because the underlying PostgreSQL version changed from 13 to 18. This guide applies whether you are upgrading to 2.x, 3.x, or any later version — the process is the same. It is recommended to always upgrade directly to the most current version.

If you follow this guide carefully, you should not lose any data in the process. However, it is **strongly recommended** to backup your system before performing the update.

## Prerequisites
- GreedyBear 1.x running with PostgreSQL 13
- Docker and Docker Compose installed
- Sufficient disk space for database dump

## Upgrade Steps
1. Open a terminal at GreedyBear's root folder
2. If GreedyBear is running, stop it: `docker compose down`
3. Navigate to the docker folder: `cd docker`
4. Remove the old postgres container: `docker rm greedybear_postgres`
5. Start an intermediary PostgreSQL 13 container: `docker run -d --name greedybear_postgres -v greedybear_postgres_data:/var/lib/postgresql/data/ --env-file env_file_postgres library/postgres:13-alpine`
6. Wait a few seconds for the container to be ready, then backup the database: `docker exec -t greedybear_postgres pg_dump -U user -d greedybear_db --no-owner > greedybear_dump.sql`
7. Stop the container: `docker container stop greedybear_postgres`
8. Remove the intermediary container: `docker rm greedybear_postgres`
9. Delete the PostgreSQL 13 data volume: `docker volume rm greedybear_postgres_data`
10. Start an intermediary PostgreSQL 18 container: `docker run -d --name greedybear_postgres -v greedybear_postgres_data:/var/lib/postgresql/data/ --env-file env_file_postgres library/postgres:18-alpine`
11. Wait a few seconds for the container to be ready, then restore the database: `cat greedybear_dump.sql | docker exec -i greedybear_postgres psql -U user -d greedybear_db`
12. Stop the intermediary container: `docker container stop greedybear_postgres`
13. Remove the intermediary container: `docker container rm greedybear_postgres`
14. Return to the root folder: `cd ..`
15. Update GreedyBear to the latest version following your standard update procedure
16. Start GreedyBear: `docker compose up`

## Verification & Cleanup
- After completing the upgrade, verify that all containers are running: `docker compose ps`
- Check if GreedyBear is accessible, functioning correctly and still contains your data
- Delete the backup file: `rm docker/greedybear_dump.sql`


