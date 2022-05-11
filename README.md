# DevOps exercise

1. Run `./script.sh`

   Assumptions: we assume that time is infinite and 'now' is not defined. So, instead of making a truly _realtime_ solution (which would require that the logs were timed in the now), we just parse the entire dataset and output firewall rules for violators.

2. Run `./awssh`
3. Do the following:
   i. Run `export FLASK_APP=core`
   ii. Run `flask db init` (after installing all the appropriate packages using your preferred package manager)
   iii. Run `flask db migrate`

### Improvements for Q3

The architectural solution has deliberately been generically designed so that platform choice and scale requirements are flexible enough. To deploy for high availability and performance, consider using an auto-scaling group (or scale set) across several availability zones or geographical data centers. Also configure the MySQL (preferably on RDS) instance to include read replicas to mimic horizontal scaling. For even better performance, a redis cache can be used to store frequently-accessed 'hot links' to reduce network trips to the database.
